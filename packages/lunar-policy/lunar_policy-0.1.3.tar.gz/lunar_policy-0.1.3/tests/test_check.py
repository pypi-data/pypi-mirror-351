import json
import tempfile
import pytest
import semver

from src.lunar_policy import Check, Path, CheckStatus
from src.lunar_policy.result import NoDataError


class TestCheck():
    @pytest.fixture(autouse=True)
    def setup_lunar_bundle(self, monkeypatch):
        test_data = {
            'merged_blob': {
                'merged_true': True,
                'merged_false': False,
                'value_in_both_roots': "hello world",
                'tricky_value': ".merged_true"
            },
            'metadata_instances': [
                {
                    'payload': {
                        'value_in_both_roots': "hello moon",
                        'value_in_one_delta': "one",
                        'value_in_two_deltas': "two_a"
                    }
                },
                {
                    'payload': {
                        'value_in_both_roots': "hello moon",
                        'value_in_two_deltas': "two_b"
                    }
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name

        monkeypatch.setenv('LUNAR_BUNDLE_PATH', temp_path)

        yield

    def test_invalid_check_initialization(self):
        with pytest.raises(ValueError):
            Check("test", data="not a SnippetData object")

    def test_description_check(self, capsys):
        with Check("test", "description") as c:
            c.assert_true(True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result["description"] == "description"

    def test_description_not_in_check(self, capsys):
        with Check("test") as c:
            c.assert_true(True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert "description" not in result

    def test_paths_in_check(self, capsys):
        with Check("test") as c:
            v = c.get(".merged_false")
            c.assert_false(v)
            c.assert_true(Path(".merged_true"))

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result["paths"] == [".merged_false", ".merged_true"]

    def test_money_path(self, capsys):
        with Check("test") as c:
            v = c.get("$.merged_false")
            c.assert_false(v)
            c.assert_true(Path("$.merged_true"))

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result["paths"] == [".merged_false", ".merged_true"]

    def test_tricky_path(self, capsys):
        with Check("test") as c:
            v = c.get("$.tricky_value")
            c.assert_equals(v, ".merged_true")

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result["paths"] == [".tricky_value"]

    def test_paths_not_in_check(self, capsys):
        with Check("test") as c:
            c.assert_true(True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert "paths" not in result

    def test_simple_value_check(self, capsys):
        with Check("test") as c:
            c.assert_true(True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)["assertions"][0]

        assert result["op"] == "true"
        assert result["args"] == ["True"]
        assert result["result"] == "pass"
        assert "failure_message" not in result

    def test_simple_path_check(self, capsys):
        with Check("test") as c:
            c.assert_true(Path(".merged_true"))

        captured = capsys.readouterr()
        result = json.loads(captured.out)["assertions"][0]

        assert result["op"] == "true"
        assert result["args"] == ["True"]
        assert result["result"] == "pass"
        assert "failure_message" not in result

    def test_multiple_assertions_in_check(self, capsys):
        with Check("test") as c:
            c.assert_true(True)
            c.assert_true(Path(".merged_true"))

        captured = capsys.readouterr()
        results = json.loads(captured.out)["assertions"]
        assert all(result["result"] == "pass" for result in results)

    def test_all_value_assertions_in_check(self, capsys):
        with Check("test") as c:
            c.assert_true(True)
            c.assert_false(False)
            c.assert_equals(1, 1)
            c.assert_greater(2, 1)
            c.assert_greater_or_equal(2, 1)
            c.assert_greater_or_equal(1, 1)
            c.assert_less(1, 2)
            c.assert_less_or_equal(1, 1)
            c.assert_contains("hello", "e")
            c.assert_match("hello", ".*ell.*")

        captured = capsys.readouterr()
        results = json.loads(captured.out)["assertions"]
        assert all(result["result"] == "pass" for result in results)

    def test_semver_comparison(self, capsys):
        with Check("test") as c:
            v1 = semver.Version.parse("1.0.0")
            v2 = semver.Version.parse("2.0.0")

            c.assert_greater_or_equal(v2, v1)
            c.assert_less_or_equal(v1, v2)

        captured = capsys.readouterr()
        results = json.loads(captured.out)["assertions"]
        assert all(result["result"] == "pass" for result in results)

    def test_can_report_no_data(self, capsys):
        with Check("test") as c:
            c.assert_true(Path(".not.a.path"))

        captured = capsys.readouterr()
        results = json.loads(captured.out)["assertions"]
        assert len(results) == 1
        assert results[0]["result"] == "no_data"

    def test_value_in_both_roots(self, capsys):
        with Check("test") as c:
            c.assert_equals(
                Path(".value_in_both_roots"),
                "hello world",
                all_instances=False
            )
            c.assert_equals(
                Path(".value_in_both_roots"),
                "hello moon",
                all_instances=True
            )

        captured = capsys.readouterr()
        results = json.loads(captured.out)
        assert all(
            result["result"] == "pass"
            for result in results["assertions"]
        )
        assert results["paths"] == [".value_in_both_roots"]

    def test_value_in_single_delta(self, capsys):
        with Check("test") as c:
            c.assert_equals(
                Path(".value_in_one_delta"),
                "one",
                all_instances=True
            )

        captured = capsys.readouterr()
        results = json.loads(captured.out)
        assert all(
            result["result"] == "pass"
            for result in results["assertions"]
        )
        assert results["paths"] == [".value_in_one_delta"]

    def test_value_in_two_deltas(self, capsys):
        with Check("test") as c:
            c.assert_contains(
                Path(".value_in_two_deltas"),
                "two",
                all_instances=True
            )

        captured = capsys.readouterr()
        results = json.loads(captured.out)
        assert all(
            result["result"] == "pass"
            for result in results["assertions"]
        )
        assert results["paths"] == [".value_in_two_deltas"]

    def test_exit_check_early_on_no_data(self, capsys):
        with Check("test") as c:
            c.assert_true(Path(".merged_true"))
            c.assert_false(Path(".not.a.path"))
            c.assert_equals("should not run", "should not run")

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert len(result["assertions"]) == 2
        assert all(a["op"] != "equals" for a in result["assertions"])

    def test_exit_check_early_on_no_data_get(self, capsys):
        with Check("test") as c:
            c.get(".not.a.path")
            c.assert_true(True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert len(result["assertions"]) == 0

    def test_suppress_on_no_data_get(self, capsys):
        with Check("test") as c:
            try:
                c.get(".not.a.path")
            except NoDataError:
                pass

            c.assert_true(True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert len(result["assertions"]) == 1

    def test_fail_check(self, capsys):
        with Check("test") as c:
            c.fail("this failed")

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert len(result["assertions"]) == 1
        assertion = result["assertions"][0]
        assert assertion["op"] == "fail"
        assert assertion["failure_message"] == "this failed"
        assert assertion["result"] == "fail"
        assert assertion["args"] == ["False"]

    def test_status_fail(self, capsys):
        with Check("test") as c:
            c.assert_true(True)
            c.fail("this failed")

        assert c.status == CheckStatus.FAIL
        assert c.failure_reasons == "this failed"

    def test_status_multiple_failures(self, capsys):
        with Check("test") as c:
            c.assert_true(True)
            c.fail("this failed")
            c.fail("this failed too")

        assert c.status == CheckStatus.FAIL
        assert c.failure_reasons == "this failed, this failed too"

    def test_status_pass(self, capsys):
        with Check("test") as c:
            c.assert_true(True)
            c.assert_false(False)

        assert c.status == CheckStatus.PASS
        assert c.failure_reasons == ""

    def test_status_no_data(self, capsys):
        with Check("test") as c:
            c.assert_true(True)
            c.fail("this failed")
            c.assert_true(Path(".not.a.path"))

        assert c.status == CheckStatus.NO_DATA
        assert c.failure_reasons == "this failed"

    def test_status_no_assertions(self, capsys):
        with Check("test") as c:
            pass

        assert c.status == CheckStatus.PASS
        assert c.failure_reasons == ""

    def test_status_unexpected_error(self, capsys):
        try:
            with Check("test"):
                raise Exception("raised")
        except Exception:
            pass

        out = capsys.readouterr().out
        res = json.loads(out)
        assert len(res["assertions"]) == 1
        assertion = res["assertions"][0]
        assert assertion["result"] == "fail"
        assert assertion["failure_message"] == "Unexpected error: raised"
