import tabula
import argparse


def convert_pdf_to_csv(kasticket: str):
    if kasticket[-4:] != '.pdf':
        print(
            f'Kon bestand "{kasticket} niet converteren: bestand is geen PDF."')
        return

    print(f'"{kasticket}" aan het converteren... ', end='')
    try:
        df = tabula.read_pdf(f'{kasticket}',
                             multiple_tables=False,
                             pages="all",
                             stream=True,
                             area=[157, 20, 817, 575],
                             columns=[65, 330, 385, 480],
                             pandas_options={'dtype': 'object'}
                             )[0]
    except FileNotFoundError:
        print(f'Kon bestand "{kasticket}" niet vinden.')
        return

    bedrag_re = r'(-?[0-9]+\.?[0-9]{0,2})'
    totaal = float(list(df.loc[df[df.columns[3]].str.contains('betalen:', na=False), df.columns[4]]
                        .str.extract(bedrag_re, expand=False))[-1])

    df = df[(df[df.columns[4]].str.fullmatch(bedrag_re, na=False))]
    df = df.astype({df.columns[3]: float, df.columns[4]: float})

    kasticket_csv = f'{kasticket[:-4]}.csv'
    df.to_csv(kasticket_csv, index=False, sep=';', decimal=',')

    som = round(df[df.columns[4]].sum(), 2)
    if som == totaal:
        print("OK.")
    else:
        print("NOK: totaal klopt niet.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Converteer Collect&Go kasticketten van PDF naar CSV.')
    parser.add_argument('kasticketten', metavar='kasticket',
                        nargs='+', help='Naam van het kasticket PDF bestand.')
    args = parser.parse_args()

    for kasticket in args.kasticketten:
        convert_pdf_to_csv(kasticket)
