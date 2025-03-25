from datetime import datetime


def resolve_date_to_timestamp(date_str, time_str) -> datetime:
    # Strings de entrada
    # date = "1/7/25 0:00"
    # hora_cupom = "19:58:47"

    # Converter a string de data para um objeto datetime
    data_base = datetime.strptime(date_str, "%d/%m/%y %H:%M")

    # Converter a string de hora para um objeto time
    hora_base = datetime.strptime(time_str, "%H:%M:%S").time()

    # Combinar a data e a hora em um único objeto datetime
    data_hora_final = datetime.combine(data_base.date(), hora_base)

    return data_hora_final