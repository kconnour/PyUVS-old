def sci_notation(number: float, decimals: int = None) -> str:
    """
    Format a number in scientific notation :math:`a x 10^b` with a specified
    number of significant figures.

    Parameters
    ----------
    number
        Hmm, I wonder what this could be...
    decimals
        The number of decimals you want. Defaults to None, which
        uses all available significant digits in :code:`number`.

    Returns
    -------
    Conventionally-formatted number.
    """
    try:
        if decimals is None:
            ndigits = len(str(number).replace('.', ''))
            coefficient, exponent = f'{number:.{ndigits-1}e}'.split('e')
        else:
            coefficient, exponent = f'{number:.{decimals}e}'.split('e')
        return fr'${coefficient} \times 10^{int(exponent)}$'
    except ValueError as ve:
        print('Number must be a float, you asshole.')


print(sci_notation('3.14159'))
