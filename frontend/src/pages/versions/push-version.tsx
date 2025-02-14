import { Button, Callout, Classes, Collapse } from "@blueprintjs/core";
import { useState } from "react";
import { useLoaderData } from "react-router-dom";
import { ActionCard } from "../../actions/action-card";
import { ActionInfo } from "../../actions/action-context";
import { ActionForm } from "../../actions/action-form";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ActionDialog } from "../../actions/action-dialog";
import { post } from "../../api/api";
import { currentInstanceApiPath } from "../../app/onshape-params";
import { ActionError } from "../../actions/action-error";
import { ActionSpinner } from "../../actions/action-spinner";
import { ActionSuccess } from "../../actions/action-success";
import { ExecuteButton } from "../../components/execute-button";
import { WorkspacePath, Workspace, toInstanceApiPath } from "../../api/path";
import { linkedParentDocumentsKey } from "../../query/query-client";
import { OpenLinkManagerButton } from "../../components/manage-links-button";
import {
    VersionDescriptionField,
    VersionNameField
} from "../../components/version-fields";
import { isVersionNameValid } from "../../common/version-utils";
import { MissingPermissionError } from "../../common/errors";
import { OnSubmitProps } from "../../common/handlers";

const actionInfo: ActionInfo = {
    title: "Push version",
    description:
        "Create a version and push it to one or more linked parent documents.",
    route: "push-version"
};

export function PushVersionCard() {
    return <ActionCard actionInfo={actionInfo} />;
}

interface PushVersionArgs {
    name: string;
    description: string;
    instancePaths: WorkspacePath[];
}

export function PushVersion() {
    const pushVersionMutationFn = async (args: PushVersionArgs) => {
        return post("/push-version" + currentInstanceApiPath(), {
            body: {
                name: args.name,
                description: args.description,
                instancesToUpdate: args.instancePaths
            }
        });
    };
    const mutation = useMutation({
        mutationKey: [actionInfo.route],
        mutationFn: pushVersionMutationFn
    });

    let actionSuccess = null;
    if (mutation.isSuccess) {
        const args = mutation.variables;
        const length = args.instancePaths.length;
        const plural = length == 1 ? "" : "s";
        const description = `Successfully pushed ${args.name} to ${length} document${plural}.`;
        actionSuccess = (
            <ActionSuccess
                message="Successfully pushed version"
                description={description}
            />
        );
    }

    let actionError = null;
    if (mutation.isError) {
        const error = mutation.error;
        if (error instanceof MissingPermissionError) {
            actionError = (
                <ActionError
                    title="Cannot push document"
                    description={error.getDescription(
                        "You don't have access to a linked document."
                    )}
                />
            );
        } else {
            actionError = <ActionError />;
        }
    }

    return (
        <ActionDialog title={actionInfo.title} isPending={mutation.isPending}>
            {mutation.isIdle && <PushVersionForm onSubmit={mutation.mutate} />}
            {mutation.isPending && (
                <ActionSpinner message="Creating and pushing version..." />
            )}
            {actionSuccess}
            {actionError}
        </ActionDialog>
    );
}

function PushVersionForm(props: OnSubmitProps<PushVersionArgs>) {
    const defaultName = useLoaderData() as string;
    const query = useQuery<Workspace[]>({ queryKey: linkedParentDocumentsKey });

    const [showInfo, setShowInfo] = useState(false);

    // Form fields and validation
    const [versionName, setVersionName] = useState(defaultName);
    const [versionDescription, setVersionDescription] = useState("");

    const enabled =
        isVersionNameValid(versionName) &&
        versionDescription.length <= 10000 &&
        query.isSuccess &&
        query.data.length > 0;

    let noParentsCallout = null;
    let preview = null;
    if (query.isSuccess) {
        if (query.data.length == 0) {
            noParentsCallout = (
                <>
                    <Callout
                        title="No linked parent documents"
                        intent="warning"
                    >
                        <p>
                            This document doesn't have any linked parents to
                            push to.
                        </p>
                        <OpenLinkManagerButton minimal={false} />
                    </Callout>
                    <br />
                </>
            );
        } else {
            preview = (
                <>
                    <Button
                        disabled={!enabled}
                        text="Explanation"
                        icon="info-sign"
                        rightIcon={showInfo ? "chevron-up" : "chevron-down"}
                        intent="primary"
                        onClick={() => setShowInfo(!showInfo)}
                    />
                    <Collapse isOpen={showInfo}>
                        <Callout intent="primary" title="Push version steps">
                            Upon execution, the following things will happen:
                            <ol className={Classes.LIST}>
                                <li>
                                    A new version named {versionName} will be
                                    created.
                                </li>
                                <li>
                                    All references to this document from the
                                    following documents will be updated to{" "}
                                    {versionName}:
                                    <ul
                                        className={Classes.LIST}
                                        style={{ listStyleType: "disc" }}
                                    >
                                        {query.data.map((document) => (
                                            <li
                                                key={toInstanceApiPath(
                                                    document
                                                )}
                                            >
                                                {document.name}
                                            </li>
                                        ))}
                                    </ul>
                                </li>
                            </ol>
                        </Callout>
                    </Collapse>
                    <br />
                </>
            );
        }
    }

    const versionNameField = (
        <VersionNameField
            versionName={versionName}
            onNameChange={setVersionName}
        />
    );

    const versionDescriptionField = (
        <VersionDescriptionField
            description={versionDescription}
            onDescriptionChange={setVersionDescription}
        />
    );

    const actions = (
        <>
            <ExecuteButton
                loading={!enabled && query.isFetching}
                disabled={!enabled}
                onSubmit={() =>
                    props.onSubmit({
                        name: versionName,
                        description: versionDescription,
                        instancePaths: query.data ?? []
                    })
                }
            />
        </>
    );
    return (
        <ActionForm description={actionInfo.description} actions={actions}>
            {preview}
            {noParentsCallout}
            {versionNameField}
            {versionDescriptionField}
        </ActionForm>
    );
}
