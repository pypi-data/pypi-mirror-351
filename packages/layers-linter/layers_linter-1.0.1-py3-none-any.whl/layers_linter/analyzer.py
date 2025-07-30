import ast
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Set

from layers_linter.config import LayerConfig, LibConfig, load_config
from layers_linter.search_modules import (
    ModulePathT,
    find_modules_in_directory,
    FilePathT,
    match_pattern,
)


@dataclass
class ImportInfo:
    module: ModulePathT
    line_number: int
    is_internal: bool  # True if it's a project module, False if it's a library


@dataclass
class Problem:
    line_number: int
    module_path: str
    imported_module: str
    layer_from: str
    layer_to: str
    code: str
    message: str

    def __str__(self):
        return (
            f"{self.module_path}:{self.line_number}: [{self.layer_from}] {self.module_path}"
            f" -> [{self.layer_to}] {self.imported_module} ({self.code}: {self.message})"
        )


class ImportVisitor(ast.NodeVisitor):
    def __init__(self, current_module: ModulePathT, all_project_modules: Set[ModulePathT]):
        self.imports: List[ImportInfo] = []
        self.current_module = current_module
        self.all_project_modules = all_project_modules
        self.inside_type_checking = False

    def process_import(self, node: ast.AST, module_name: ModulePathT):
        if self.inside_type_checking:
            return

        is_internal = module_name in self.all_project_modules
        self.imports.append(ImportInfo(module_name, node.lineno, is_internal))

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            name = alias.name
            self.process_import(node, ModulePathT(name))

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.level > 0:
            if not self.current_module:
                return
            parts = self.current_module.split(".")
            level = node.level
            if level > len(parts):
                return
            base_parts = parts[:-level]
            module = node.module
            if not module:
                return
            new_parts = base_parts + [module]
            module_name = ModulePathT(".".join(new_parts))
        else:
            module_name = ModulePathT(node.module)
        self.process_import(node, module_name)

    def visit_If(self, node: ast.If):
        if isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
            old_flag = self.inside_type_checking
            self.inside_type_checking = True
            for stmt in node.body:
                self.visit(stmt)
            self.inside_type_checking = old_flag
            for stmt in node.orelse:
                self.visit(stmt)
        else:
            self.generic_visit(node)


def collect_imports(all_project_modules, modules_list) -> Dict[ModulePathT, List[ImportInfo]]:
    module_imports: Dict[ModulePathT, List[ImportInfo]] = defaultdict(list)
    for path, module_path in modules_list:
        with open(path) as f:
            content = f.read()
        tree = ast.parse(content)
        visitor = ImportVisitor(module_path, all_project_modules)
        visitor.visit(tree)
        module_imports[module_path].extend(visitor.imports)

    return module_imports


def analyze_dependencies(
    project_root: Path,
    layers: Dict[str, LayerConfig],
    libs: Dict[str, LibConfig],
    exclude_modules: List[str],
) -> List[Problem]:
    modules_list = find_modules_in_directory(
        FilePathT(project_root), patterns=None, exclude_patterns=exclude_modules
    )
    all_project_modules = set(module_path for _, module_path in modules_list)

    module_to_layers: Dict[ModulePathT, List[str]] = defaultdict(list)
    for _, module_path in modules_list:
        for layer_name, layer_info in layers.items():
            for pattern in layer_info.contains_modules:
                if match_pattern(module_path, pattern):
                    module_to_layers[module_path].append(layer_name)
                    break

    module_imports = collect_imports(all_project_modules, modules_list)

    problems = []

    for module_path, imports in module_imports.items():
        layers_a = module_to_layers.get(module_path, [])
        for import_info in imports:
            imported_module = import_info.module
            lineno = import_info.line_number

            if not import_info.is_internal:
                continue

            layers_b = module_to_layers.get(imported_module, [])

            if not layers_a or not layers_b:
                continue

            allowed = False
            for la_name in layers_a:
                for lb_name in layers_b:
                    la = layers[la_name]
                    lb = layers[lb_name]

                    # Downstream check: layer A can only depend on those specified in download.
                    downstream_ok = True
                    if la.downstream is not None:
                        if lb_name not in la.downstream:
                            downstream_ok = False

                    # Verification Upstream: layer B can only be used in Upstream.
                    upstream_ok = True
                    if lb.upstream is not None:
                        if la_name not in lb.upstream:
                            upstream_ok = False

                    if downstream_ok and upstream_ok:
                        allowed = True
                        break
                if allowed:
                    break

            if not allowed:
                for la_name in layers_a:
                    for lb_name in layers_b:
                        problems.append(
                            Problem(
                                line_number=lineno,
                                module_path=module_path,
                                imported_module=imported_module,
                                layer_from=la_name,
                                layer_to=lb_name,
                                code="LA001",
                                message=f"Invalid dependency from layer '{la_name}' to layer '{lb_name}'",
                            )
                        )

    # Check library dependencies
    for module_path, imports in module_imports.items():
        layers_a = module_to_layers.get(module_path, [])

        for import_info in imports:
            imported_module = import_info.module
            lineno = import_info.line_number

            # Skip if it's not a library import
            if import_info.is_internal:
                continue

            # Find if this is a known library
            matching_libs = []
            for lib_name in libs:
                if imported_module == lib_name or imported_module.startswith(f"{lib_name}."):
                    matching_libs.append(lib_name)

            for lib_name in matching_libs:
                lib_config = libs[lib_name]

                # If library has no restrictions, skip
                if lib_config.upstream is None:
                    continue

                # Check if any of the module's layers are allowed to use this library
                allowed = False
                for layer_name in layers_a:
                    if layer_name in lib_config.upstream:
                        allowed = True
                        break

                if not allowed:
                    layers_str = "', '".join(layers_a)
                    problems.append(
                        Problem(
                            line_number=lineno,
                            module_path=module_path,
                            imported_module=imported_module,
                            layer_from="none",
                            layer_to="none",
                            code="LA020",
                            message=f"Layers [{layers_str}] cannot use restricted library '{lib_name}'",
                        )
                    )

    return problems


def run_linter(project_root: Path, config_path: Path) -> List[Problem]:
    layers, libs, exclude_modules = load_config(config_path)
    return analyze_dependencies(project_root, layers, libs, exclude_modules)
