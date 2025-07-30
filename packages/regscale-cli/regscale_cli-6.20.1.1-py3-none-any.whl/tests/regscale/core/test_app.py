"""
Test the Application class used by the RegScale CLI.
"""

import os
from unittest.mock import patch, MagicMock

from requests import Response

from regscale.core.app.application import Application


class TestApplication:
    test_config_file = "test_application_config.yaml"
    os.environ["REGSCALE_CONFIG_FILE"] = test_config_file
    app = Application()
    app.config_file = test_config_file
    test_domain = "https://example.com"
    test_token = "Bearer test_token"

    def teardown_method(self, method):
        """
        Remove the test config file after each test
        """
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)

    def test_init(self):
        assert isinstance(self.app, Application)
        assert isinstance(self.app, Application)
        assert self.app.config != {}
        assert self.app.local_config is True
        assert self.app.running_in_airflow is False

    def test_singleton(self):
        test_config = {"key": "value"}
        app2 = Application()
        assert self.app == app2
        app3 = Application(config=test_config)
        assert test_config["key"] == app3["key"]
        assert app3 != self.app
        assert app3 != app2

    @patch("regscale.core.app.internal.login.parse_user_id_from_jwt")
    @patch("requests.get")
    def test_fetch_config_from_regscale_success(self, mock_get, mock_parse_user_id):
        mock_parse_user_id.return_value = "test_user_id"
        mock_response = MagicMock()
        mock_response.json.return_value = {"cliConfig": "key: value"}
        mock_get.return_value = mock_response
        config = self.app._fetch_config_from_regscale(config=self.app.config)
        assert "domain" in config
        assert config["userId"] == "test_user_id"
        assert config["key"] == "value"

    @patch("regscale.core.app.internal.login.parse_user_id_from_jwt")
    @patch("requests.get")
    def test_fetch_config_from_regscale_success_with_envars(self, mock_get, mock_parse_user_id):
        mock_parse_user_id.return_value = "test_user_id"
        mock_response = MagicMock()
        mock_response.json.return_value = {"cliConfig": "key: value"}
        mock_get.return_value = mock_response
        os.environ["REGSCALE_DOMAIN"] = self.test_domain
        os.environ["REGSCALE_TOKEN"] = self.test_token
        config = self.app._fetch_config_from_regscale(config={})
        assert config["domain"] == self.test_domain
        assert config["token"] == self.test_token
        assert config["userId"] == "test_user_id"
        assert config["key"] == "value"

    @patch("requests.get")
    def test_fetch_config_from_regscale_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = "Not found."
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        os.environ["REGSCALE_DOMAIN"] = self.test_domain
        os.environ["REGSCALE_TOKEN"] = self.test_token
        empty_config = self.app._fetch_config_from_regscale()
        assert empty_config == {}
        with patch.object(self.app.logger, "error") as mock_logger_error:
            config = self.app._fetch_config_from_regscale(config=self.app.config)
            mock_logger_error.assert_called_once()
            assert config == {}

    def test_gen_config(self):
        self.app.local_config = True
        self.app.config_file = "test_gen_config.yaml"
        config = self.app._gen_config()
        assert "key" not in config
        assert "domain" in config
        assert "token" in config

        small_config = {"key": "value", "domain": self.test_domain}
        config = self.app._gen_config(small_config)
        assert config["key"] == "value"
        assert config["domain"] == self.test_domain
        os.remove(self.app.config_file)

    def test_gen_config_airflow(self):
        self.app.running_in_airflow = True
        with patch.object(self.app, "_get_airflow_config", return_value={"key": "value"}):
            config = self.app._gen_config()
            assert config == {"key": "value"}

    def test_gen_config_with_provided_config(self):
        self.app.local_config = True
        config = {"key": "value"}
        with patch.object(self.app, "_get_env", return_value={"env_key": "env_value"}):
            with patch.object(self.app, "verify_config", return_value={"key": "value", "env_key": "env_value"}):
                with patch.object(self.app, "save_config") as mock_save_config:
                    result = self.app._gen_config(config)
                    assert result == {"key": "value", "env_key": "env_value"}
                    mock_save_config.assert_called_once()

    def test_gen_config_without_local_config(self):
        self.app.local_config = False
        with patch.object(self.app, "_get_env", return_value={"env_key": "env_value"}):
            with patch.object(self.app, "verify_config", return_value={"env_key": "env_value"}):
                with patch.object(self.app, "save_config") as mock_save_config:
                    result = self.app._gen_config()
                    assert result == {"env_key": "env_value"}
                    mock_save_config.assert_called_once()

    def test_gen_config_with_file_config(self):
        self.app.local_config = True
        with patch.object(self.app, "_get_conf", return_value={"file_key": "file_value"}):
            with patch.object(self.app, "_get_env", return_value={"env_key": "env_value"}):
                with patch.object(
                    self.app, "verify_config", return_value={"file_key": "file_value", "env_key": "env_value"}
                ):
                    with patch.object(self.app, "save_config") as mock_save_config:
                        result = self.app._gen_config()
                        assert result == {"file_key": "file_value", "env_key": "env_value"}
                        mock_save_config.assert_called_once()

    def test_gen_config_scanner_error(self):
        from yaml.scanner import ScannerError

        self.app.local_config = True
        with patch.object(self.app, "_get_conf", side_effect=ScannerError):
            with patch.object(self.app, "save_config") as mock_save_config:
                result = self.app._gen_config()
                assert result == self.app.template
                # called twice because the first call is to save the default config
                mock_save_config.assert_called_once()

    def test_get_airflow_config_with_dict(self):
        config = {"key": "value"}
        with patch.object(self.app, "_fetch_config_from_regscale", return_value={"key": "value"}):
            result = self.app._get_airflow_config(config)
            assert result == {"key": "value"}

    def test_get_airflow_config_with_str(self):
        config = "{'key': 'value'}"
        with patch.object(self.app, "_fetch_config_from_regscale", return_value={"key": "value"}):
            result = self.app._get_airflow_config(config)
            assert result == {"key": "value"}

    def test_get_airflow_config_with_env_vars(self):
        os.environ["REGSCALE_TOKEN"] = self.test_token
        os.environ["REGSCALE_DOMAIN"] = self.test_domain
        with patch.object(self.app, "_fetch_config_from_regscale", return_value={"key": "value"}):
            result = self.app._get_airflow_config()
            assert result == {"key": "value"}

    def test_get_airflow_config_no_config(self):
        os.environ["REGSCALE_TOKEN"] = ""
        os.environ["REGSCALE_DOMAIN"] = ""
        result = self.app._get_airflow_config()
        assert result is None

        os.environ["REGSCALE_TOKEN"] = self.test_token
        os.environ["REGSCALE_DOMAIN"] = self.test_domain
        with patch.object(
            self.app, "_fetch_config_from_regscale", return_value={"token": self.test_token, "domain": self.test_domain}
        ):
            result = self.app._get_airflow_config()
            assert result["token"] == self.test_token
            assert result["domain"] == self.test_domain

    def test_get_airflow_config_invalid_json(self):
        config = "{'key': 'value'"
        with patch.object(self.app.logger, "debug") as mock_logger_debug:
            result = self.app._get_airflow_config(config)
            assert result is None
            mock_logger_debug.assert_called()

    def test_get_env_with_matching_keys(self):
        with patch.object(self.app, "template", {"key1": "value1", "key2": "value2"}):
            with patch.dict(os.environ, {"key1": "env_value1", "key2": "env_value2"}):
                result = self.app._get_env()
                assert result == {"key1": "env_value1", "key2": "env_value2"}

    def test_get_env_with_no_matching_keys(self):
        with patch.object(self.app, "template", {"key1": "value1", "key2": "value2"}):
            with patch.dict(os.environ, {"key3": "env_value3"}):
                result = self.app._get_env()
                assert result == {"key1": "value1", "key2": "value2"}

    def test_get_env_with_key_error(self):
        with patch.object(self.app, "template", {"key1": "value1", "key2": "value2"}):
            with patch.dict(os.environ, {"key1": "env_value1"}):
                with patch.object(self.app.logger, "error") as mock_logger_error:
                    result = self.app._get_env()
                    assert result == {"key1": "env_value1", "key2": "value2"}
                    mock_logger_error.assert_not_called()

    def test_get_env_with_template_match(self):
        with patch.object(self.app, "template", {"key1": "value1", "key2": "value2"}):
            with patch.dict(os.environ, {"key1": "value1", "key2": "value2"}):
                result = self.app._get_env()
                assert result == {"key1": "value1", "key2": "value2"}
                assert self.app.templated is True

    def test_get_env_without_template_match(self):
        with patch.object(self.app, "template", {"key1": "value1", "key2": "value2"}):
            with patch.dict(os.environ, {"key1": "env_value1"}):
                result = self.app._get_env()
                assert result == {"key1": "env_value1", "key2": "value2"}
                assert self.app.templated is False

    def test_get_conf(self):
        self.app.config_file = self.test_config_file
        self.app = Application(config={"key": "value"})
        with patch("yaml.safe_load", return_value={"key": "value"}):
            config = self.app._get_conf()
            assert config == {"key": "value"}
        with patch("yaml.safe_load", side_effect=FileNotFoundError):
            config = self.app._get_conf()
            assert config is None

    def test_save_config(self):
        from regscale.core.app.utils.api_handler import APIHandler

        self.app.config_file = "test_save_config.yaml"
        test_config = {"key": "value"}
        with patch.object(self.app, "running_in_airflow", True):
            self.app.save_config(test_config)
            config = self.app.load_config()
            assert "key" not in config

        self.app.running_in_airflow = False
        self.app.save_config(test_config)
        config = self.app.load_config()
        assert config is not None
        assert config["key"] == "value"
        assert "domain" not in config

        test_api_handler = APIHandler()
        self.app.api_handler = test_api_handler
        test_config = {"api_handler": "testing_api_handler", "domain": self.test_domain}
        self.app.save_config(test_config)
        config = self.app.load_config()
        assert config["api_handler"] == "testing_api_handler"
        assert test_api_handler.domain == self.test_domain
        assert test_api_handler.config == test_config

        with patch.object(self.app.logger, "error") as mock_logger_error:
            with patch("yaml.dump", side_effect=OSError):
                self.app.save_config({})
                mock_logger_error.assert_called_once()

        os.remove(self.app.config_file)

    def test_get_regscale_license(self):
        with patch("requests.get"):
            regscale_license = self.app.get_regscale_license(MagicMock())
            assert isinstance(regscale_license, MagicMock)

    def test_load_config(self):
        self.app.config_file = self.test_config_file
        with patch("yaml.safe_load", side_effect=FileNotFoundError):
            config = self.app.load_config()
            assert config == {}

        self.app.save_config({"key": "value"})
        config = self.app.load_config()
        assert config == {"key": "value"}

    def test_get_regscale_license_with_config(self):
        api = MagicMock()
        api.config = {"domain": self.test_domain}
        api.get.return_value = Response()
        self.app.config = api.config

        with patch.object(self.app, "retrieve_domain", return_value=self.test_domain):
            response = self.app.get_regscale_license(api)
            api.get.assert_called_once_with(url="https://example.com/api/config/getlicense")
            assert isinstance(response, Response)

    def test_get_regscale_license_without_config(self):
        api = MagicMock()
        api.config = {"domain": self.test_domain}
        api.get.return_value = Response()
        self.app.config = None

        with patch.object(self.app, "_gen_config", return_value={"domain": self.test_domain}):
            with patch.object(self.app, "retrieve_domain", return_value=self.test_domain):
                response = self.app.get_regscale_license(api)
                api.get.assert_called_once_with(url="https://example.com/api/config/getlicense")
                assert isinstance(response, Response)

    def test_get_regscale_license_with_airflow_config(self):
        api = MagicMock()
        api.config = None
        api.get.return_value = Response()
        self.app.config = None
        self.app.running_in_airflow = True

        with patch.object(self.app, "_get_airflow_config", return_value={"domain": self.test_domain}):
            with patch.object(self.app, "retrieve_domain", return_value=self.test_domain):
                response = self.app.get_regscale_license(api)
                api.get.assert_called_once_with(url="https://example.com/api/config/getlicense")
                assert isinstance(response, Response)

    def test_get_regscale_license_with_suppressed_exception(self):
        import requests

        api = MagicMock()
        api.config = {"domain": self.test_domain}
        api.get.side_effect = requests.RequestException
        self.app.config = {"domain": self.test_domain}

        with patch.object(self.app, "retrieve_domain", return_value=self.test_domain):
            response = self.app.get_regscale_license(api)
            api.get.assert_called_once_with(url="https://example.com/api/config/getlicense")
            assert response is None

    def test_retrieve_domain(self):
        possible_envars = ["REGSCALE_DOMAIN", "PLATFORM_HOST", "domain"]
        for envar in possible_envars:
            with patch("os.environ", {envar: self.test_domain}):
                domain = self.app.retrieve_domain()
                assert domain == self.test_domain
            with patch("os.environ", {envar: "www.example.com"}):
                domain = self.app.retrieve_domain()
                assert domain == self.app.template["domain"]

    def test_verify_config(self):
        template = {"key": "value"}
        config = {"key": "other_value"}
        updated_config = self.app.verify_config(template, config)
        assert updated_config == {"key": "other_value"}

    def test_verify_config_with_missing_keys(self):
        template = {"key1": "value1", "key2": "value2"}
        config = {"key1": "value1"}
        expected_config = {"key1": "value1", "key2": "value2"}
        updated_config = self.app.verify_config(template, config)
        assert updated_config == expected_config

    def test_verify_config_with_type_mismatch(self):
        template = {"key1": "value1", "key2": 2}
        config = {"key1": "value1", "key2": "wrong_type"}
        expected_config = {"key1": "value1", "key2": 2}
        updated_config = self.app.verify_config(template, config)
        assert updated_config == expected_config

    def test_verify_config_with_nested_dict(self):
        template = {"key1": "value1", "key2": {"subkey1": "subvalue1"}}
        config = {"key1": "value1", "key2": {"subkey1": "wrong_value"}}
        expected_config = {"key1": "value1", "key2": {"subkey1": "wrong_value"}}
        updated_config = self.app.verify_config(template, config)
        assert updated_config == expected_config

    def test_verify_config_with_additional_keys(self):
        template = {"key1": "value1"}
        config = {"key1": "value1", "key2": "value2"}
        expected_config = {"key1": "value1", "key2": "value2"}
        updated_config = self.app.verify_config(template, config)
        assert updated_config == expected_config

    def test_verify_config_with_empty_config(self):
        template = {"key1": "value1", "key2": "value2"}
        config = {}
        expected_config = {"key1": "value1", "key2": "value2"}
        updated_config = self.app.verify_config(template, config)
        assert updated_config == expected_config

    def test_getitem(self):
        self.app.config = {"key": "value"}
        assert self.app["key"] == "value"

    def test_setitem(self):
        self.app.config = {}
        self.app["key"] = "value"
        assert self.app.config == {"key": "value"}

    def test_delitem(self):
        self.app.config = {"key": "value"}
        del self.app["key"]
        assert self.app.config == {}

    def test_iter(self):
        self.app.config = {"key1": "value1", "key2": "value2"}
        assert list(self.app) == ["key1", "key2"]

    def test_len(self):
        self.app.config = {"key1": "value1", "key2": "value2"}
        assert len(self.app) == 2

    def test_contains(self):
        self.app.config = {"key": "value"}
        assert "key" in self.app
        assert "nonexistent_key" not in self.app
