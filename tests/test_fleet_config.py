#!/usr/bin/env python3
"""
Unit test suite for Coolify VPS Fleet Manager configuration, scripts, and GUI.
Ensures JSON schemas, file paths, syntax validation, mover script, GUI HUD, and templates pass with 0 errors.
"""

import json
import os
import unittest


class TestCoolifyFleetConfig(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_example = os.path.join(self.base_dir, "config", "vps-fleet.example.json")
        self.install_script = os.path.join(self.base_dir, "scripts", "install-coolify.sh")
        self.deploy_script = os.path.join(self.base_dir, "scripts", "deploy-all-vps.sh")
        self.ps_script = os.path.join(self.base_dir, "scripts", "deploy-all-vps.ps1")
        self.mover_script = os.path.join(self.base_dir, "scripts", "move-resource.py")
        self.workflow_file = os.path.join(self.base_dir, ".github", "workflows", "deploy-coolify.yml")
        self.launcher_file = os.path.join(self.base_dir, "launcher.py")
        self.portable_run = os.path.join(self.base_dir, "Run.bat")
        self.portable_gui_run = os.path.join(self.base_dir, "Run-GUI.bat")
        self.gui_server = os.path.join(self.base_dir, "gui", "server.py")
        self.gui_html = os.path.join(self.base_dir, "gui", "index.html")
        self.compose_dir = os.path.join(self.base_dir, "templates", "compose")

    def test_example_config_exists_and_valid_json(self):
        self.assertTrue(os.path.exists(self.config_example), "config/vps-fleet.example.json must exist")
        with open(self.config_example, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("servers", data)
        self.assertIsInstance(data["servers"], list)
        self.assertGreater(len(data["servers"]), 0)

        for s in data["servers"]:
            self.assertIn("name", s)
            self.assertIn("ip", s)
            self.assertIn("role", s)
            self.assertIn(s["role"], ["control-plane", "worker"])

    def test_install_script_contains_security_checks(self):
        self.assertTrue(os.path.exists(self.install_script), "install-coolify.sh must exist")
        with open(self.install_script, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("set -euo pipefail", content)
        self.assertIn("cdn.coollabs.io/coolify/install.sh", content)
        self.assertIn("check_privileges", content)
        self.assertIn("configure_firewall", content)

    def test_deploy_and_mover_scripts_exist(self):
        self.assertTrue(os.path.exists(self.deploy_script), "deploy-all-vps.sh must exist")
        self.assertTrue(os.path.exists(self.ps_script), "deploy-all-vps.ps1 must exist")
        self.assertTrue(os.path.exists(self.mover_script), "move-resource.py must exist")
        self.assertTrue(os.path.exists(self.workflow_file), "deploy-coolify.yml must exist")
        self.assertTrue(os.path.exists(self.launcher_file), "launcher.py must exist")
        self.assertTrue(os.path.exists(self.portable_run), "Run.bat must exist")

    def test_gui_components_exist(self):
        self.assertTrue(os.path.exists(self.gui_server), "gui/server.py must exist")
        self.assertTrue(os.path.exists(self.gui_html), "gui/index.html must exist")
        self.assertTrue(os.path.exists(self.portable_gui_run), "Run-GUI.bat must exist")

    def test_portable_launcher_uses_relative_path(self):
        with open(self.portable_run, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("%~dp0", content, "Run.bat must use dynamic %~dp0 to be 100% relocatable")

        with open(self.portable_gui_run, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("%~dp0", content, "Run-GUI.bat must use dynamic %~dp0 to be 100% relocatable")

    def test_compose_templates_exist(self):
        expected_templates = [
            "fullstack-node.yml",
            "python-fastapi.yml",
            "n8n-automation.yml"
        ]
        for t in expected_templates:
            t_path = os.path.join(self.compose_dir, t)
            self.assertTrue(os.path.exists(t_path), f"Template {t} must exist")
            with open(t_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("version:", content)
            self.assertIn("services:", content)


if __name__ == "__main__":
    unittest.main()
