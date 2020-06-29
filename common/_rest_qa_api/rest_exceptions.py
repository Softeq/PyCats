class MethodNotSupportedByEndpoint(Exception):
    def __init__(self, item):
        self.message = f"This Endpoint does not support '{item}' method"
        super().__init__(self, self.message)

    def __str__(self):
        return self.message


class DataclassNameError(Exception):
    def __init__(self, class_name):
        self.message = f"Child dataclass should be private. Use _{class_name} or __{class_name} instead of {class_name}"
        super().__init__(self, self.message)

    def __str__(self):
        return self.message


class MissingDecoratorError(Exception):
    def __init__(self, class_name):
        self.message = f"Child dataclass {class_name} should have @scaf_dataclass decorator"
        super().__init__(self, self.message)

    def __str__(self):
        return self.message


class RestResponseValidationError(Exception):
    def __init__(self, response):
        self.message = ""
        self.default_errors = response.errors["default"]
        self.custom_errors = response.errors["custom"]
        if self.default_errors:
            self.message += f"\n{'#' * 80}\nDEFAULT RESPONSE VALIDATION FAILED BASED ON THE PROVIDED MODEL." \
                            f"\n{'#' * 80}\n" + "\n".join(f"Field '{'->'.join(str(field) for field in item[0])}',"
                                                          f" expected value '{item[1]}', but got '{item[2]}' "
                                                          for item in self.default_errors)
        if self.custom_errors:
            self.message += f"\n{'#' * 40}\nCUSTOM RESPONSE VALIDATION FAILED.\n{'#' * 40}\n" + \
                            "\n".join(f"Checker '{error[0] if isinstance(error[0], str) else error[0].__name__}' "
                                      f"failed with error: {error[1]} " for error in self.custom_errors)

        if self.message:
            self.message += f"\n{'#' * 40}\nVALIDATED RESPONSE\n{'#' * 40}\n{response}"

        super().__init__(self, self.message)

    def __str__(self):
        return self.message
