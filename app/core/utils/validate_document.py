def validate_cpf(cpf: str) -> bool:
    """Validates a CPF (Brazilian Individual Taxpayer Registry)."""
    if len(cpf) != 11 or cpf in {cpf[0] * 11 for cpf in cpf}:
        return False

    def calculate_digit(cpf, weight):
        total = sum(int(digit) * weight for digit, weight in zip(cpf, range(weight, 1, -1)))
        remainder = (total * 10) % 11
        return str(remainder if remainder < 10 else 0)

    return cpf[-2:] == calculate_digit(cpf[:9], 10) + calculate_digit(cpf[:10], 11)


def validate_cnpj(cnpj: str) -> bool:
    """Validates a CNPJ (Brazilian National Registry of Legal Entities)."""
    if len(cnpj) != 14 or cnpj in {cnpj[0] * 14 for cnpj in cnpj}:
        return False

    def calculate_digit(cnpj, weights):
        total = sum(int(digit) * weight for digit, weight in zip(cnpj, weights))
        remainder = total % 11
        return str(0 if remainder < 2 else 11 - remainder)

    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights2 = [6] + weights1

    return cnpj[-2:] == calculate_digit(cnpj[:12], weights1) + calculate_digit(cnpj[:13], weights2)
