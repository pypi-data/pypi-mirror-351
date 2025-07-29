#!/usr/bin/env python3
"""
Script pour lancer les tests de tous les packages installés
Supporte unittest, pytest, nose, et gère les fixtures
"""

import json
import subprocess
import sys
from pathlib import Path

import pkg_resources


class PackageTester:
    def __init__(self, timeout=60, verbose=True):
        self.timeout = timeout
        self.verbose = verbose
        self.results = {}

    def find_test_directories(self, package_location):
        """Trouve les répertoires de tests dans un package"""
        test_dirs = []
        package_path = Path(package_location)

        # Patterns communs pour les tests
        test_patterns = ["test*", "tests*", "*_test", "*_tests", "Test*", "Tests*", "*Test", "*Tests"]

        for pattern in test_patterns:
            test_dirs.extend(package_path.glob(f"**/{pattern}"))

        # Filtrer pour ne garder que les répertoires
        return [d for d in test_dirs if d.is_dir() and any(d.glob("*.py"))]

    def detect_test_framework(self, test_dir):
        """Détecte le framework de test utilisé"""
        frameworks = []

        # Chercher des fichiers de configuration
        config_files = {
            "pytest": ["pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini"],
            "unittest": ["unittest.cfg"],
            "nose": ["nose.cfg", ".noserc"],
        }

        for framework, configs in config_files.items():
            if any((test_dir / config).exists() for config in configs):
                frameworks.append(framework)

        # Analyser les imports dans les fichiers de test
        for test_file in test_dir.glob("**/*.py"):
            try:
                with open(test_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "import pytest" in content or "from pytest" in content:
                        frameworks.append("pytest")
                    elif "import unittest" in content or "from unittest" in content:
                        frameworks.append("unittest")
                    elif "import nose" in content or "from nose" in content:
                        frameworks.append("nose")
            except Exception:
                continue

        return list(set(frameworks)) or ["pytest"]  # pytest par défaut

    def run_pytest(self, test_dir, package_name):
        """Lance pytest avec gestion des fixtures"""
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(test_dir),
            "-v",
            "--tb=short",
            "--maxfail=5",
            f"--junit-xml=test_results_{package_name}.xml",
        ]

        # Chercher des conftest.py pour les fixtures
        if (test_dir / "conftest.py").exists():
            cmd.extend(["--confcutdir", str(test_dir)])

        return self._run_command(cmd, test_dir)

    def run_unittest(self, test_dir, package_name):
        """Lance unittest discover"""
        cmd = [sys.executable, "-m", "unittest", "discover", "-s", str(test_dir), "-p", "test*.py", "-v"]

        return self._run_command(cmd, test_dir)

    def run_nose(self, test_dir, package_name):
        """Lance nose tests"""
        cmd = [sys.executable, "-m", "nose", str(test_dir), "-v"]

        return self._run_command(cmd, test_dir)

    def _run_command(self, cmd, cwd):
        """Exécute une commande avec timeout"""
        try:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=self.timeout)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "stdout": "", "stderr": f"Timeout après {self.timeout}s", "returncode": -1}
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e), "returncode": -2}

    def test_package(self, package):
        """Teste un package spécifique"""
        package_name = package.project_name
        package_location = package.location

        if self.verbose:
            print(f"\n=== Testing {package_name} ===")
            print(f"Location: {package_location}")

        # Chercher les répertoires de tests
        test_dirs = self.find_test_directories(package_location)

        if not test_dirs:
            self.results[package_name] = {"status": "no_tests", "message": "Aucun répertoire de test trouvé"}
            return

        package_results = []

        for test_dir in test_dirs:
            if self.verbose:
                print(f"Testing directory: {test_dir}")

            # Détecter le framework
            frameworks = self.detect_test_framework(test_dir)

            for framework in frameworks:
                if self.verbose:
                    print(f"Using framework: {framework}")

                # Lancer les tests selon le framework
                if framework == "pytest":
                    result = self.run_pytest(test_dir, package_name)
                elif framework == "unittest":
                    result = self.run_unittest(test_dir, package_name)
                elif framework == "nose":
                    result = self.run_nose(test_dir, package_name)
                else:
                    continue

                package_results.append({"test_dir": str(test_dir), "framework": framework, "result": result})

                if self.verbose:
                    status = "✓ PASS" if result["success"] else "✗ FAIL"
                    print(f"  {status} ({framework})")
                    if not result["success"] and result["stderr"]:
                        print(f"  Error: {result['stderr'][:200]}...")

        self.results[package_name] = {"status": "tested", "results": package_results}

    def test_all_packages(self, exclude_patterns=None):
        """Teste tous les packages installés"""
        if exclude_patterns is None:
            exclude_patterns = ["pip", "setuptools", "wheel", "pkg-resources"]

        packages = list(pkg_resources.working_set)
        total = len(packages)

        print(f"Trouvé {total} packages installés")
        print("Exclusions:", exclude_patterns)

        for i, package in enumerate(packages, 1):
            if any(pattern in package.project_name.lower() for pattern in exclude_patterns):
                if self.verbose:
                    print(f"[{i}/{total}] Skipping {package.project_name}")
                continue

            if self.verbose:
                print(f"[{i}/{total}] Testing {package.project_name}")

            try:
                self.test_package(package)
            except Exception as e:
                self.results[package.project_name] = {"status": "error", "message": str(e)}
                if self.verbose:
                    print(f"  Error: {e}")

    def generate_report(self, output_file=None):
        """Génère un rapport des résultats"""
        report = {
            "summary": {
                "total_packages": len(self.results),
                "tested": sum(1 for r in self.results.values() if r["status"] == "tested"),
                "no_tests": sum(1 for r in self.results.values() if r["status"] == "no_tests"),
                "errors": sum(1 for r in self.results.values() if r["status"] == "error"),
            },
            "details": self.results,
        }

        if output_file:
            with open(output_file, "w") as f:
                json.dump(report, f, indent=2)

        return report


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test tous les packages installés")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout par test en secondes")
    parser.add_argument("--quiet", action="store_true", help="Mode silencieux")
    parser.add_argument("--output", type=str, help="Fichier de sortie JSON")
    parser.add_argument("--exclude", nargs="*", default=["pip", "setuptools", "wheel"], help="Packages à exclure")

    args = parser.parse_args()

    tester = PackageTester(timeout=args.timeout, verbose=not args.quiet)

    try:
        tester.test_all_packages(exclude_patterns=args.exclude)
        report = tester.generate_report(args.output)

        print("\n" + "=" * 50)
        print("RÉSUMÉ")
        print("=" * 50)
        print(f"Packages testés: {report['summary']['tested']}")
        print(f"Sans tests: {report['summary']['no_tests']}")
        print(f"Erreurs: {report['summary']['errors']}")

        if args.output:
            print(f"Rapport détaillé sauvé dans: {args.output}")

    except KeyboardInterrupt:
        print("\nInterrompu par l'utilisateur")
        sys.exit(1)


if __name__ == "__main__":
    main()
