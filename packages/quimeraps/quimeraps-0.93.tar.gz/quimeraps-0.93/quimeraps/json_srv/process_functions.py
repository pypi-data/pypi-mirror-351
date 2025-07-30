import os
import sys
from quimeraps.json_srv import logging
from typing import Dict, List, Optional, Union, Any
import subprocess
import json
import tempfile
import base64
import locale
from quimeraps import __VERSION__, DATA_DIR
from pyreportjasper import report, config as jasper_config  # type: ignore [import]
import ghostscript  # type: ignore [import]
from quimeraps.json_srv import data as data_module


LOGGER = logging.getLogger(__name__)
TIMEOUT = 500


def get_single_process_file():
    current_file = os.path.abspath(__file__)
    current_dir = os.path.abspath(os.path.join(os.path.dirname(current_file), ".."))
    return os.path.join(current_dir, "single_proccess.py")


def launch_single_proccess(typo, data):
    global TIMEOUT
    file_name = get_single_process_file()
    # Se genera fichero tmp random

    file_tmp = tempfile.mkstemp(".json")
    file_data_json = tempfile.mkstemp(".json")
    file_error = tempfile.mkstemp(".txt")

    file_tmp_name = file_tmp[1]
    file_data_json_name = file_data_json[1]
    output_file_error = file_error[1]
    with open(file_data_json_name, "w") as f:
        f.write(json.dumps(data))

    array_command = ["python3", file_name, typo, file_data_json_name, file_tmp_name]
    LOGGER.warning("Comando %s" % " ".join(array_command))
    process = subprocess.run(
        array_command,
        timeout=TIMEOUT,
        # stderr=output_file_error,
    )
    LOGGER.warning("Resultado %s en %s" % (process.returncode, file_tmp_name))
    if process.returncode == 0:
        with open(file_tmp_name, "rb") as f:
            return json.load(f)
    else:
        raise Exception("Error en proceso:")


def print_proceso(json_data):
    return launch_single_proccess("print", json_data)


def sync_proceso(json_data):
    return launch_single_proccess("sync", json_data)


def processSyncRequest(json_data) -> Dict[str, Any]:
    """Process sync request."""

    group_name = json_data["group_name"]
    result = processSync(group_name, json_data["arguments"])
    return {"result": 1 if result else 0, "data": result}


def processSync(group_name, arguments) -> bool:
    """Process sync"""
    result = ""
    try:
        if group_name == "resources":
            group_name = "%s/../resources"
        sync_folder = os.path.join(os.path.abspath(DATA_DIR), group_name)
        LOGGER.warning("Sync folder %s" % sync_folder)
        if not os.path.exists(sync_folder):
            LOGGER.warning("Making folder %s" % sync_folder)
            os.mkdir(sync_folder)

        file_type = "%ss" % arguments["file_type"]

        type_folder = os.path.join(sync_folder, file_type)
        if not os.path.exists(type_folder):
            LOGGER.warning("Making folder %s" % type_folder)
            os.mkdir(type_folder)
        file_path = os.path.join(type_folder, arguments["file_name"])
        file_path_compiled = file_path.replace(".jrxml", ".jasper")
        if arguments["file_delete"] == "1":
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(file_path):
                result = (
                    "No se ha podido eliminar el fichero %s" % arguments["file_name"]
                )
            else:
                if file_type == "subreports":
                    if os.path.exists(file_path_compiled):
                        os.remove(file_path_compiled)
                    if os.path.exists(file_path_compiled):
                        result = (
                            "No se ha podido eliminar el fichero %s"
                            % file_path_compiled
                        )
        else:
            file = open(file_path, "wb")
            file.write(base64.decodebytes(arguments["file_data"].encode()))
            file.close()

            if file_type == "subreports" and file_path.endswith(".jrxml"):
                # compilamos el subreport.
                config = jasper_config.Config()
                config.output = file_path_compiled
                config.writeJasper = True
                instance = report.Report(config, file_path)
                instance.compile()
            # result = "Fichero %s instalado" % file_path

    except Exception as error:
        result = str(error)

    LOGGER.warning("devolviendo %s" % result)
    return result


def processPrintRequest(kwargs) -> Dict[str, Any]:
    """Process print request."""
    is_error: bool = False
    data_or_str: Union[str, List[Any]] = ""
    return_base64: bool = (
        "return_base64" in kwargs.keys() and kwargs["return_base64"] == 1
    )

    if "type" in kwargs.keys():
        type_ = kwargs["type"]
        # LOGGER.warning("NEW %s!" % (type_))
        if type_ == "new_job":
            data_or_str = printerRequest(kwargs["arguments"])
            is_error = not os.path.exists(data_or_str)
        elif type_ == "alive":
            data_or_str = aliveRequest()
        elif type_ == "data":
            data_or_str = dataRequest(kwargs["arguments"])
        else:
            LOGGER.warning("Unknown request %s!" % (type_))

    else:
        is_error = True
        data_or_str = "type field is not defined"

    LOGGER.warning(
        "Result: %s, data: %s, base_64: %s"
        % ("Failed" if is_error else "Ok", data_or_str, return_base64)
    )
    return {
        "result": 1 if is_error else 0,
        "data": (
            fileToBase64(data_or_str) if return_base64 and not is_error else data_or_str
        ),
    }


def fileToBase64(file_name) -> str:
    """Return base64 file content."""

    file = open(file_name, "rb")
    result = base64.b64encode(file.read())
    file.close()
    return result.decode()


def aliveRequest() -> str:
    """Return a alive string."""
    return __VERSION__


def dataRequest(kwargs) -> List[Any]:
    """Return data from database connection."""
    CONN = data_module.SQLiteClass()
    result: str = ""

    # table_name = kwargs['table'] if 'table' in kwargs.keys() else ""
    mode = kwargs["mode"]

    # fields = kwargs['fields'] if 'fields' in kwargs.keys() else ['*']
    # pk = kwargs['pk'] if 'pk' in kwargs.keys() else '1 = 1'
    # values = kwargs['values'] if 'values' in kwargs.keys() else []
    raw_text = kwargs["raw"] if "raw" in kwargs.keys() else ""
    with_response = (
        True
        if "with_response" in kwargs.keys() and kwargs["with_response"] == 1
        else False
    )
    result = "ok"
    try:
        if mode == "raw":
            try:
                query_cursor = CONN.executeQuery(raw_text)
                # print("CALLING!", raw_text)
                if with_response:
                    result = query_cursor.fetchall()
                query_cursor.close()
            except Exception as error:
                result = str(error)
        else:
            result = "unknown mode (%s)" % mode
    except Exception as error:
        result = str(error)

    return [{"error": result}] if isinstance(result, str) else result


def printerRequest(kwargs) -> str:
    """Print requests."""
    result = ""
    kwargs_names = kwargs.keys()

    only_pdf = "only_pdf" in kwargs_names and kwargs["only_pdf"] == 1
    group_name = kwargs["group_name"] if "group_name" in kwargs_names else None
    pdf_name = kwargs["pdf_name"] if "pdf_name" in kwargs_names else None

    if not only_pdf:
        for name in ["printer"]:
            if name not in kwargs_names:
                result = "%s field not specified" % name

    if "model" not in kwargs_names:
        kwargs["model"] = ""

    if "data" not in kwargs_names:
        kwargs["data"] = []

    if "report_name" not in kwargs_names:
        kwargs["report_name"] = ""

    if not result:
        if "cut" not in kwargs_names:
            kwargs["cut"] = False
        if "open_cash_drawer" not in kwargs_names:
            kwargs["open_cash_drawer"] = False

        try:
            result = launchPrinter(
                kwargs["printer"] if not only_pdf else "",
                kwargs["model"],
                kwargs["cut"],
                kwargs["open_cash_drawer"],
                kwargs["data"],
                pdf_name,
                only_pdf,
                group_name,
                kwargs["report_name"],
                kwargs["params"] if "params" in kwargs_names else {},
                int(kwargs["copies"]) if "copies" in kwargs_names else None,
            )
        except Exception as error:
            result = str(error)

    return result


def resolvePrinter(printer_alias: str):
    """Resolve printer name using alias."""
    CONN = data_module.SQLiteClass()
    printer_cursor = CONN.executeQuery(
        "SELECT name,cut,cash_drawer FROM printers WHERE alias='%s'" % printer_alias
    )
    if printer_cursor.rowcount:
        result = printer_cursor.fetchone()
        printer_cursor.close()
        return result

    return None


def resolveModel(model_alias: str):
    """Resolve model file usign alias."""
    CONN = data_module.SQLiteClass()
    model_cursor = CONN.executeQuery(
        "SELECT name,copies FROM models WHERE alias='%s'" % model_alias
    )
    if model_cursor.rowcount:
        result = model_cursor.fetchone()
        model_cursor.close()

        return result

    return None


def launchPrinter(
    printer_alias: str,
    model_alias: str,
    cut: bool,
    open_cd: bool,
    data: List[Any],
    pdf_name=None,
    only_pdf=False,
    group_name=None,
    model_name="",
    params: Dict = {},
    copies: Optional[int] = None,
) -> str:
    """Print a request."""
    result = ""
    # resolver nombre impresora
    printer_data = resolvePrinter(printer_alias) if not only_pdf else None
    model_data = None
    if not printer_data and not only_pdf:
        result = "Printer alias (%s) doesn't exists!" % printer_alias
        LOGGER.warning(result)

    # resolver nomber model
    if not result and not model_name:
        model_data = resolveModel(model_alias)
        if not model_data:
            result = "Model alias (%s) doesn't exists!" % model_alias
            LOGGER.warning(result)

    if not result and not data:
        result = "Data (%s) is empty" % data
        LOGGER.warning(result)

    if not result:  # Si no hay fallo previo
        # crear request
        printer_name = printer_data[0] if not only_pdf else None
        cut_command: Optional[str] = (
            printer_data[1] if cut and printer_data[1] else None
        )
        open_command: Optional[str] = (
            printer_data[2] if open_cd and printer_data[2] else None
        )
        model_name = model_data[0] if not model_name and model_data else model_name
        num_copies = int(model_data[1]) if model_data and model_data[1] else 1
        if copies is not None:
            LOGGER.warning("Overriding copies (%s) with %s" % (num_copies, copies))
            num_copies = int(copies)

        reports_dir = os.path.join(
            os.path.abspath(DATA_DIR), group_name if group_name else "", "reports"
        )
        if not os.path.exists(reports_dir):
            LOGGER.warning("Making reports folder (%s)" % reports_dir)
            os.mkdir(reports_dir)

        input_file = "%s" % os.path.join(reports_dir, "%s" % model_name)
        if not input_file.lower().endswith(".jrxml"):
            input_file += ".jrxml"

        if not os.path.exists(input_file):
            result = "Model (%s) doesn't exists!" % input_file
            LOGGER.warning(result)
        else:
            output_file = (
                os.path.join(tempfile.gettempdir(), pdf_name)
                if pdf_name
                else tempfile.mktemp()
            )
            output_file_pdf = output_file + "%s" % (
                ".pdf" if not output_file.lower().endswith(".pdf") else ""
            )

            data_dumps = json.dumps({"query": {"registers": data}})
            # generamos temporal con datos json
            temp_json_file = tempfile.mktemp(".json")
            file_ = open(temp_json_file, "w", encoding="UTF-8")
            file_.write(data_dumps)
            file_.close()

            if not os.path.exists(temp_json_file):
                result = "JSON file (%s) doesn't exists!" % temp_json_file
                LOGGER.warning(result)
            else:

                # LOGGER.info("Starting...")
                # LOGGER.info("JSON: %s" % temp_json_file)
                # LOGGER.info("JASPER: %s" % input_file)
                # LOGGER.info("OUTPUT: %s" % output_file_pdf)

                resources_folder = os.path.abspath(
                    os.path.join(os.path.dirname(input_file), "..", "resources")
                )
                resource_files = None
                if os.path.exists(resources_folder):
                    resource_files = os.path.abspath(resources_folder)
                    LOGGER.info("** RESOURCES FOLDER: %s" % resource_files)
                try:
                    config = jasper_config.Config()
                    config.input = input_file
                    config.output = output_file
                    config.dataFile = temp_json_file
                    config.jvm_maxmem = "16384M"
                    config.locale = (
                        params["REPORT_LOCALE"]
                        if "REPORT_LOCALE" in params.keys()
                        else "es_ES"
                    )
                    config.jsonLocale = (
                        params["JSON_LOCALE"]
                        if "JSON_LOCALE" in params.keys()
                        else "en_US"
                    )
                    config.dbType = "json"
                    config.jsonQuery = "query.registers"
                    config.resource = resource_files
                    config.params = {
                        "SUBREPORT_DIR": "%s%s"
                        % (
                            os.path.join(
                                os.path.abspath(DATA_DIR),
                                group_name if group_name else "",
                                "subreports",
                            ),
                            "\\" if sys.platform.startswith("win") else "/",
                        )
                    }
                    if params:
                        for param_key, param_value in params.items():
                            # LOGGER.debug(
                            #    "Adding param %s = %s" % (param_key, param_value)
                            # )
                            if param_key in ["REPORT_LOCALE"]:
                                continue
                            config.params[param_key] = param_value

                    # LOGGER.info("Starting reports server %s" % config.input)
                    instance = report.Report(config, config.input)
                    LOGGER.info("Using %s to fill %s" % (temp_json_file, config.input))
                    # LOGGER.warning("Default locale %s" % instance.defaultLocale)
                    # LOGGER.warning("Current locale %s" % instance.config.locale)
                    instance.fill()
                    LOGGER.info("Filling done")
                    LOGGER.info("Exporting to PDF")
                    instance.export_pdf()
                    LOGGER.info("Export done")
                    if not only_pdf:
                        for num in range(num_copies):
                            LOGGER.info(
                                "Sendign copy %s, printer: %s, model: %s"
                                % (num + 1, printer_name, model_name)
                            )
                            result = sendToPrinter(printer_name, output_file_pdf)

                            # lanza corte
                            if not result and cut_command:
                                temp_cut_file: str = tempfile.mktemp(".esc_command")
                                file_cut = open(temp_cut_file, "b")
                                file_cut.write(cut_command.encode())
                                file_cut.close()
                                result = sendToPrinter(printer_name, temp_cut_file)

                            if result:
                                break
                        # lanza cajon
                        if not result and open_command:
                            temp_open_file: str = tempfile.mktemp(".esc_command")
                            file_cut = open(temp_open_file, "b")
                            file_cut.write(open_command.encode())
                            file_cut.close()
                            result = sendToPrinter(printer_name, temp_open_file)
                    result = output_file_pdf

                except Exception as error:
                    result = "Error: %s. Saliendo" % str(error)
                    LOGGER.warning(result)
                    raise Exception(result)
    # LOGGER.info(result)
    return result


def sendToPrinter(printer: str, file_name):
    """Send document to printer."""
    result = ""
    LOGGER.debug("Sending to printer '%s' -> %s" % (printer, file_name))
    if sys.platform.startswith("win"):
        args = [
            "-dPrinted",
            "-dBATCH",
            "-dNOSAFER",
            "-dNOPAUSE",
            "-dNOPROMPT" "-q",
            "-dNumCopies#1",
            "-sDEVICE#mswinpr2",
            f'-sOutputFile#"%printer%{printer}"',
            f'"{file_name}"',
        ]

        try:
            encoding = locale.getpreferredencoding()
            args = [a.encode(encoding) for a in args]
            LOGGER.debug("Launching GS command with arguments %s" % args)
            LOGGER.debug(ghostscript.Ghostscript(*args))
        except Exception as error:
            result = str(error)

    else:
        try:
            os.system("lp -d %s %s" % (printer, file_name))
        except Exception as error:
            result = str(error)

    return result


def quimera_log():
    """Recoge los datos del fichero /var/log/quimeraps.log y los devuevle en base64"""

    file_name = "/var/log/quimeraps.log"
    try:
        if os.path.exists(file_name):
            with open(file_name, "rb") as f:
                log_data = f.read()
        else:
            log_data = b"No existe el fichero %s" % file_name

    except Exception as e:
        log_data = str(e).encode()

    return base64.b64encode(log_data).decode()
