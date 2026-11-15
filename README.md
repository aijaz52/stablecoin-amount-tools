# stablecoin-amount-tools

A small, dependency-free Python module for exact conversion between human-readable decimal token amounts and integer base units. It uses string operations only: no floating-point arithmetic, network access, wallet/signing, payments, chain inference, or exchange-rate lookups.

## Usage

Requires Python 3.9+.

```sh
python stablecoin_amounts.py to-units 1.25 --decimals 6
# 1250000

python stablecoin_amounts.py from-units 1250000 --decimals 6
# 1.25

python -m unittest discover -s tests -v
```

`--decimals` is always required and must be an integer from 0 through 255. Amounts and units are ASCII decimal strings (`0`–`9`); Unicode numeral lookalikes are rejected. Negative values, exponent notation, non-integer base units, boolean/non-integer decimal settings, and malformed input are rejected.

If a human amount has more fractional digits than `decimals`, extra digits are allowed only when they are all zero (for example, `1.2300` with 2 decimals). Any non-zero excess digit is rejected; the tool never silently rounds. To keep memory and runtime predictable, each input is limited to 100,000 digits excluding a decimal point.

The library API is available as `stablecoin_amounts.to_units(amount, decimals)` and `stablecoin_amounts.from_units(units, decimals)`. Both return canonical decimal strings and raise `ValueError` for invalid input.

## Limitations

This utility does not validate token contracts, addresses, networks, chain-specific decimal metadata, balances, exchange rates, transaction status, or the identity of a recipient. It is not a wallet, payment processor, signing tool, or financial advice. No claim is made about adoption, audit status, or production readiness.

## Development disclosure

This project was created with AI assistance and reviewed through local tests and CLI smoke checks. That disclosure is not a claim of independent security audit or production suitability.

## License

MIT; see [LICENSE](LICENSE).
