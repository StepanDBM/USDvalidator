from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DiscoveryNode:
    name: str
    path: Path
    directories: dict[str, "DiscoveryNode"] = field(default_factory=dict)
    reports: list[object] = field(default_factory=list)

    @property
    def file_count(self):
        return len(self.reports) + sum(node.file_count for node in self.directories.values())

    @property
    def passed_count(self):
        return sum(bool(report.publish_passed) for report in self.reports) + sum(
            node.passed_count for node in self.directories.values()
        )

    @property
    def failed_count(self):
        return self.file_count - self.passed_count


def build_report_tree(reports, root=None):
    reports = tuple(reports)
    if not reports:
        return DiscoveryNode("Batch", Path())

    paths = [Path(report.source_path).expanduser().resolve() for report in reports]
    root_path = Path(root).expanduser().resolve() if root else common_directory(paths)
    root_node = DiscoveryNode(root_path.name or str(root_path), root_path)

    for report, path in sorted(zip(reports, paths), key=lambda pair: pair[1].as_posix().lower()):
        parent = root_node
        try:
            relative = path.relative_to(root_path)
        except ValueError:
            relative = Path(path.anchor) / path.relative_to(path.anchor)
        current_path = root_path
        for part in relative.parts[:-1]:
            current_path /= part
            parent = parent.directories.setdefault(part, DiscoveryNode(part, current_path))
        parent.reports.append(report)
    return root_node


def common_directory(paths):
    paths = [path.parent if path.suffix else path for path in paths]
    common = paths[0]
    for path in paths[1:]:
        while common != common.parent and not _is_relative_to(path, common):
            common = common.parent
    return common


def _is_relative_to(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False
