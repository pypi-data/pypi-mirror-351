from unittest import TestCase

from voter_tools.pa import errors as pa_errors


class InvalidAccessKeyErrorTestCase(TestCase):
    # This is silly, I'll admit.

    def test_default_message(self):
        """Test the default message."""
        err = pa_errors.InvalidAccessKeyError()
        self.assertTrue("Invalid" in str(err))

    def test_custom_message(self):
        """Test a custom message."""
        err = pa_errors.InvalidAccessKeyError("Custom message")
        self.assertTrue("Custom message" in str(err))


class APIValidationErrorTestCase(TestCase):
    def test_message(self):
        """Test the message."""
        details_1 = pa_errors.APIErrorDetails(
            type="test1", msg="fun1", loc=("foo", "bar")
        )
        details_2 = pa_errors.APIErrorDetails(
            type="test2", msg="fun2", loc=("biz", "baz")
        )
        err = pa_errors.APIValidationError([details_1, details_2])
        self.assertTrue("foo" in str(err))
        self.assertTrue("bar" in str(err))
        self.assertTrue("biz" in str(err))
        self.assertTrue("baz" in str(err))

    def test_errors(self):
        details_1 = pa_errors.APIErrorDetails(
            type="test1", msg="fun1", loc=("foo", "bar")
        )
        details_2 = pa_errors.APIErrorDetails(
            type="test2", msg="fun2", loc=("biz", "baz")
        )
        expected = (details_1, details_2)
        err = pa_errors.APIValidationError([details_1, details_2])
        self.assertEqual(err.errors(), expected)

    def test_json(self):
        details_1 = pa_errors.APIErrorDetails(
            type="test1", msg="fun1", loc=("foo", "bar")
        )
        details_2 = pa_errors.APIErrorDetails(
            type="test2", msg="fun2", loc=("biz", "baz")
        )
        expected = [
            {"type": "test1", "msg": "fun1", "loc": ["foo", "bar"]},
            {"type": "test2", "msg": "fun2", "loc": ["biz", "baz"]},
        ]
        err = pa_errors.APIValidationError([details_1, details_2])
        self.assertEqual(err.json(), expected)

    def test_merge(self):
        details_1 = pa_errors.APIErrorDetails(
            type="test1", msg="fun1", loc=("foo", "bar")
        )
        details_2 = pa_errors.APIErrorDetails(
            type="test2", msg="fun2", loc=("biz", "baz")
        )
        expected = (details_1, details_2)
        err_1 = pa_errors.APIValidationError([details_1])
        err_2 = pa_errors.APIValidationError([details_2])
        err = err_1.merge(err_2)
        self.assertEqual(err.errors(), expected)

    def test_simple(self):
        err = pa_errors.APIValidationError.simple("field", "type", "msg")
        expected_details = pa_errors.APIErrorDetails(
            type="type", msg="msg", loc=("field",)
        )
        self.assertEqual(err.errors(), (expected_details,))

    def test_unexpected(self):
        err = pa_errors.APIValidationError.unexpected()
        self.assertEqual(err.errors()[0].type, "unexpected")

    def test_unexpected_code(self):
        err = pa_errors.APIValidationError.unexpected("code")
        self.assertTrue("code" in err.errors()[0].msg)


class MergeErrorsTestCase(TestCase):
    def test_no_errors(self):
        err = pa_errors.merge_errors(())
        self.assertIsNone(err)

    def test_single_validation_error(self):
        error_1 = pa_errors.APIValidationError.simple("field", "type", "msg")
        merged = pa_errors.merge_errors((error_1,))
        self.assertIsInstance(merged, pa_errors.APIValidationError)

    def test_single_nonvalidation_error(self):
        error_1 = pa_errors.InvalidAccessKeyError()
        merged = pa_errors.merge_errors((error_1,))
        self.assertIsInstance(merged, pa_errors.InvalidAccessKeyError)

    def test_multiple_validation_errors(self):
        error_1 = pa_errors.APIValidationError.simple("field1", "type1", "msg1")
        error_2 = pa_errors.APIValidationError.simple("field2", "type2", "msg2")
        merged = pa_errors.merge_errors((error_1, error_2))
        self.assertIsInstance(merged, pa_errors.APIValidationError)
        assert isinstance(merged, pa_errors.APIValidationError)
        expected = (error_1.errors()[0], error_2.errors()[0])
        self.assertEqual(merged.errors(), expected)

    def test_multiple_validation_errors_and_one_nonvalidation_error(self):
        error_1 = pa_errors.APIValidationError.simple("field1", "type1", "msg1")
        error_2 = pa_errors.APIValidationError.simple("field2", "type2", "msg2")
        error_3 = pa_errors.InvalidAccessKeyError()
        merged = pa_errors.merge_errors((error_1, error_2, error_3))
        self.assertIsInstance(merged, pa_errors.InvalidAccessKeyError)

    def test_first_nonvalidation_error_wins(self):
        error_1 = pa_errors.APIValidationError.simple("field", "type", "msg")
        error_2 = pa_errors.InvalidAccessKeyError()
        error_3 = pa_errors.ProgrammingError()
        merged = pa_errors.merge_errors((error_1, error_2, error_3))
        self.assertIsInstance(merged, pa_errors.InvalidAccessKeyError)


class BuildErrorForCodesTestCase(TestCase):
    def test_empty_codes(self):
        err = pa_errors.build_error_for_codes(())
        self.assertIsNone(err)

    def test_unknown_code(self):
        err = pa_errors.build_error_for_codes(("unknown",))
        self.assertIsInstance(err, pa_errors.APIValidationError)
        assert isinstance(err, pa_errors.APIValidationError)
        self.assertTrue("unknown" in err.errors()[0].msg)

    def test_access_key_error(self):
        err = pa_errors.build_error_for_codes(("VR_WAPI_InvalidAccessKey",))
        self.assertIsInstance(err, pa_errors.InvalidAccessKeyError)

    def test_single_validation_error(self):
        err = pa_errors.build_error_for_codes(("VR_WAPI_InvalidOVRDLFormat",))
        self.assertIsInstance(err, pa_errors.APIValidationError)
        assert isinstance(err, pa_errors.APIValidationError)
        self.assertEqual(len(err.errors()), 1)
        self.assertTrue(err.errors()[0].loc == ("drivers_license",))

    def test_multiple_validation_errors(self):
        err = pa_errors.build_error_for_codes(
            ("VR_WAPI_InvalidOVRDLFormat", "VR_WAPI_InvalidOVRPreviousCounty")
        )
        self.assertIsInstance(err, pa_errors.APIValidationError)
        assert isinstance(err, pa_errors.APIValidationError)
        self.assertEqual(len(err.errors()), 2)
        self.assertTrue(err.errors()[0].loc == ("drivers_license",))
        self.assertTrue(err.errors()[1].loc == ("previous_county",))

    def test_multiple_validation_errors_and_one_nonvalidation_error(self):
        err = pa_errors.build_error_for_codes(
            (
                "VR_WAPI_InvalidOVRDLFormat",
                "VR_WAPI_InvalidOVRPreviousCounty",
                "VR_WAPI_InvalidAction",
            )
        )
        self.assertIsInstance(err, pa_errors.ProgrammingError)
