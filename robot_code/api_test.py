from library.api import api_base, conf, api_path
from library.api.endpoints import documents, assemblies


def main():
    api = api_base.ApiKey(logging=False)
    config = conf.Config()
    target = config.documents["target"]
    base = config.documents["base"]

    document = documents.get_document_elements(api, target)
    target_path = document["Assembly 1"]

    base_document = documents.get_document_elements(api, base)
    base_path = base_document["Part Studio 1"]

    base_path.workspace_or_version = "v"
    base_path.workspace_id = documents.get_latest_version(api, base_path)["id"]

    print(assemblies.add_parts_to_assembly(api, target_path, base_path))

    # ref = documents.get_external_references(api, target_path)[
    #     "elementExternalReferences"
    # ][target_path.element_id]
    # for path in ref:
    #     print(path)
    #     if not path["isOutOfDate"]:
    #         continue
    #     current_path = api_path.ElementPath(
    #         api_path.DocumentPath(path["documentId"], path["id"], "v"),
    #         path["referencedElements"][0],
    #     )
    #     documents.update_to_latest_reference(api, target_path, current_path)


if __name__ == "__main__":
    main()
