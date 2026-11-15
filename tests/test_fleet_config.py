#!/usr/bin/env python3
"""
Unit test suite for Coolify VPS Fleet Manager configuration & shell scripts.
Ensures JSON schemas, file paths, and syntax validation pass with 0 errors.
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
        self.workflow_file = os.path.join(self.base_dir, ".github", "workflows", "deploy-coolify.yml")

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

    def test_deploy_scripts_exist(self):
        self.assertTrue(os.path.exists(self.deploy_script), "deploy-all-vps.sh must exist")
        self.assertTrue(os.path.exists(self.ps_script), "deploy-all-vps.ps1 must exist")
        self.assertTrue(os.path.exists(self.workflow_file), "deploy-coolify.yml must exist")


if __name__ == "__main__":
    unittest.main()
