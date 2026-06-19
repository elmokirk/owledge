from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

from . import core, modules, pi, quality, skills


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def library_root(args: argparse.Namespace) -> pathlib.Path:
    return pathlib.Path(getattr(args, "library_root", ".")).expanduser().resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Owlib standalone knowledge hub")
    sub = parser.add_subparsers(dest="command", required=True)

    init_p = sub.add_parser("init")
    init_p.add_argument("--library-root", required=True)

    register_p = sub.add_parser("register-project")
    register_p.add_argument("--library-root", default=".")
    register_p.add_argument("--path", required=True)
    register_p.add_argument("--name")

    sync_p = sub.add_parser("sync")
    sync_p.add_argument("--library-root", default=".")
    sync_p.add_argument("--reviewed-only", action="store_true")

    index_p = sub.add_parser("index")
    index_p.add_argument("--library-root", default=".")

    parallels_p = sub.add_parser("find-parallels")
    parallels_p.add_argument("--library-root", default=".")

    report_p = sub.add_parser("report")
    report_p.add_argument("--library-root", default=".")

    doctor_p = sub.add_parser("doctor")
    doctor_p.add_argument("--library-root", default=".")

    quality_p = sub.add_parser("quality")
    quality_p.add_argument("--library-root", default=".")
    quality_p.add_argument("--package-root", default="")

    benchmark_p = sub.add_parser("benchmark")
    benchmark_p.add_argument("--library-root", default=".")
    benchmark_p.add_argument("--record-counts", default="10,100,1000")

    module_p = sub.add_parser("module")
    module_sub = module_p.add_subparsers(dest="module_command", required=True)
    for name in ["list", "status"]:
        p = module_sub.add_parser(name)
        p.add_argument("--library-root", default=".")
    install_p = module_sub.add_parser("install")
    install_p.add_argument("--library-root", default=".")
    install_p.add_argument("module_name")
    remove_p = module_sub.add_parser("remove")
    remove_p.add_argument("--library-root", default=".")
    remove_p.add_argument("module_name")

    skill_p = sub.add_parser("skill")
    skill_sub = skill_p.add_subparsers(dest="skill_command", required=True)
    export_p = skill_sub.add_parser("export")
    export_p.add_argument("--runtime", required=True, choices=sorted(skills.RUNTIME_FILES))
    export_p.add_argument("--output-dir", default="")
    export_p.add_argument("--library-root", default="")

    growth_p = sub.add_parser("growth")
    growth_sub = growth_p.add_subparsers(dest="growth_command", required=True)
    for name in ["scan", "suggest"]:
        p = growth_sub.add_parser(name)
        p.add_argument("--library-root", default=".")
    promote_p = growth_sub.add_parser("promote")
    promote_p.add_argument("--library-root", default=".")
    promote_p.add_argument("--title", required=True)
    promote_p.add_argument("--source", default="")

    pi_p = sub.add_parser("pi")
    pi_sub = pi_p.add_subparsers(dest="pi_command", required=True)
    for name in ["report", "find-parallels", "recurring-errors", "suggest-central-projects", "redteam"]:
        p = pi_sub.add_parser(name)
        p.add_argument("--library-root", default=".")

    args = parser.parse_args(argv)

    try:
        if args.command == "init":
            print_json(core.init_library(library_root(args)))
        elif args.command == "register-project":
            print_json(core.register_project(library_root(args), pathlib.Path(args.path), args.name))
        elif args.command == "sync":
            print_json(core.sync_library(library_root(args), reviewed_only=args.reviewed_only))
        elif args.command == "index":
            print_json(core.build_index(library_root(args)))
        elif args.command == "find-parallels":
            print_json(core.find_parallel_candidates(library_root(args)))
        elif args.command == "report":
            print_json(core.write_library_report(library_root(args)))
        elif args.command == "doctor":
            print_json(quality.doctor(library_root(args)))
        elif args.command == "quality":
            package_root = pathlib.Path(args.package_root).expanduser().resolve() if args.package_root else pathlib.Path(__file__).resolve().parents[2]
            print_json(quality.quality_gate(library_root(args), package_root))
        elif args.command == "benchmark":
            counts = [int(item.strip()) for item in args.record_counts.split(",") if item.strip()]
            print_json(quality.benchmark(library_root(args), counts))
        elif args.command == "module":
            root = library_root(args)
            if args.module_command == "list":
                print_json(modules.list_modules(root))
            elif args.module_command == "install":
                print_json(modules.install_module(root, args.module_name))
            elif args.module_command == "remove":
                print_json(modules.remove_module(root, args.module_name))
            elif args.module_command == "status":
                print_json(modules.module_status(root))
        elif args.command == "skill":
            output = pathlib.Path(args.output_dir).expanduser().resolve() if args.output_dir else None
            if output is None and args.library_root:
                output = pathlib.Path(args.library_root).expanduser().resolve() / "skills" / "exports" / args.runtime
            if output is None:
                output = pathlib.Path.cwd() / "owlib-skill-export" / args.runtime
            print_json(skills.export_skills(args.runtime, output))
        elif args.command == "growth":
            root = library_root(args)
            if args.growth_command == "scan":
                print_json(core.growth_scan(root))
            elif args.growth_command == "suggest":
                print_json(core.growth_suggest(root))
            elif args.growth_command == "promote":
                print_json(core.growth_promote_candidate(root, args.title, args.source))
        elif args.command == "pi":
            root = library_root(args)
            if args.pi_command == "report":
                print_json(pi.pi_report(root))
            elif args.pi_command == "find-parallels":
                print_json(core.find_parallel_candidates(root))
            elif args.pi_command == "recurring-errors":
                print_json(pi.recurring_errors(root))
            elif args.pi_command == "suggest-central-projects":
                print_json(pi.central_project_candidates(root))
            elif args.pi_command == "redteam":
                print_json(pi.redteam(root))
        return 0
    except Exception as exc:
        print_json({"passed": False, "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
