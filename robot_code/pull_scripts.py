import pathlib

from library.api import api, call_api, conf
from library.transform import transform


def insert_code(function: str, code: list[str]) -> str:
    lines = function.splitlines()
    for stmt in code:
        lines.insert(2, stmt)
    return "\n".join(lines)


def main():
    onshape = api.Api(logging=False)
    config = conf.Config()
    backend_path = config.get_document("backend")
    if not backend_path:
        raise ValueError("Failed to find backend?")
    studio_path_map = call_api.get_studios(onshape, backend_path)

    json_code = call_api.get_code(onshape, studio_path_map["toJson.fs"].path)
    assembly_script_code = call_api.get_code(
        onshape, studio_path_map["assemblyScript.fs"].path
    )

    functions = [
        transform.to_lambda(transform.extract_function(json_code, name))
        for name in ["toJson", "toArray", "toMap", "toValue"]
    ]
    parse_id = transform.to_lambda(
        transform.extract_function(assembly_script_code, "parseId")
    )
    all = functions
    all.append(parse_id)

    evaluate_functions = {
        name: transform.extract_function(assembly_script_code, name)
        for name in ["parseBase", "parseTarget"]
    }
    evaluate_functions = {
        key: "function" + (value.strip().removeprefix("function " + key))
        for key, value in evaluate_functions.items()
    }
    parse_base = insert_code(evaluate_functions["parseBase"], all)
    parse_target = insert_code(evaluate_functions["parseTarget"], functions)

    out = "export const parseBaseScript = `{}`\nexport const parseTargetScript = `{}`\n".format(
        parse_base, parse_target
    ).replace(
        "\\", "\\\\"
    )
    pathlib.Path("./assembly-script.ts").write_text(out)


if __name__ == "__main__":
    main()
