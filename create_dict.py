from src.dict_codes_descr import main_write_dict

if __name__ == "__main__":
    main_write_dict('https://www.indec.gob.ar/ftp/cuadros/economia/cin_III_2023.xls',
                    report="pii",
                      key_column="SDMX",
                      value_column="Codigo BDP")