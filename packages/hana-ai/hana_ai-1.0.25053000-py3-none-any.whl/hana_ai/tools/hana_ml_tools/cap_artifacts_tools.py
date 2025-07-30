"""
This module contains the functions to generate CAP artifacts.

The following class is available:

    * :class `CAPArtifactsTool`
"""

#pylint: disable=too-many-function-args

import json
import logging
import os
import tempfile
from pathlib import Path
import platform
from typing import Optional, Type
from pydantic import BaseModel, Field

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool

from hana_ml import ConnectionContext
from hana_ml.model_storage import ModelStorage
from hana_ml.artifacts.generators.hana import HANAGeneratorForCAP

logger = logging.getLogger(__name__)

class CAPArtifactsInput(BaseModel):
    """
    The input schema for the CAPArtifactsTool.
    """
    name: str = Field(description="the name of the model in model storage. If not provided, ask the user. Do not guess.")
    version: int = Field(description="the version of the model in model storage. If not provided, ask the user. Do not guess.")
    project_name: str = Field(description="the name of the project for CAP project. If not provided, ask the user. Do not guess.")
    output_dir: str = Field(description="the output directory for CAP project. If not provided, ask the user. Do not guess.")
    namespace: Optional[str] = Field(description="the namespace for CAP project, it is optional", default=None)
    cds_gen: Optional[bool] = Field(description="whether to generate CDS files for CAP project, it is optional", default=None)
    tudf: Optional[bool] = Field(description="whether to generate table UDF for CAP project, it is optional", default=None)
    archive: Optional[bool] = Field(description="whether to archive the generated artifacts, it is optional", default=None)

class CAPArtifactsForBASInput(BaseModel):
    """
    The input schema for the CAPArtifactsTool.
    """
    name: str = Field(description="the name of the model in model storage. If not provided, ask the user. Do not guess.")
    version: int = Field(description="the version of the model in model storage. If not provided, ask the user. Do not guess.")
    cds_gen: Optional[bool] = Field(description="whether to generate CDS files for CAP project, it is optional", default=None)
    tudf: Optional[bool] = Field(description="whether to generate table UDF for CAP project, it is optional", default=None)
    archive: Optional[bool] = Field(description="whether to archive the generated artifacts, it is optional", default=None)


class CAPArtifactsTool(BaseTool):
    """
    This tool generates CAP artifacts for a given model.

    Parameters
    ----------
    connection_context : ConnectionContext
        Connection context to the HANA database.

    Returns
    -------
    str
        The directory to the generated CAP artifacts.

        .. note::

            args_schema is used to define the schema of the inputs as follows:

            .. list-table::
                :widths: 15 50
                :header-rows: 1

                * - Field
                  - Description
                * - name
                  - The name of the model in model storage. If not provided, ask the user. Do not guess.
                * - version
                  - The version of the model in model storage. If not provided, ask the user. Do not guess.
                * - project_name
                  - The name of the project for CAP project. If not provided, ask the user. Do not guess.
                * - output_dir
                  - The output directory for CAP project. If not provided, ask the user. Do not guess.
                * - namespace
                  - The namespace for CAP project, it is optional.
                * - cds_gen
                  - Whether to generate CDS files for CAP project, it is optional.
                * - tudf
                  - Whether to generate table UDF for CAP project, it is optional.
                * - archive
                  - Whether to archive the generated artifacts, it is optional.
    """
    name: str = "cap_artifacts"
    """Name of the tool."""
    description: str = "To generate CAP artifacts for a given model from model storage. "
    """Description of the tool."""
    connection_context: ConnectionContext = None
    """Connection context to the HANA database."""
    args_schema: Type[BaseModel] = CAPArtifactsInput
    return_direct: bool = False

    def __init__(
        self,
        connection_context: ConnectionContext,
        return_direct: bool = False
    ) -> None:
        super().__init__(  # type: ignore[call-arg]
            connection_context=connection_context,
            return_direct=return_direct
        )

    def _run(
        self, name: str, version: str, project_name: str, output_dir: str, namespace: Optional[str] = None,
        cds_gen: Optional[bool] = False, tudf: Optional[bool] = False, archive: Optional[bool] = False,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        ms = ModelStorage(connection_context=self.connection_context)
        model = ms.load_model(name, version)

        generator = HANAGeneratorForCAP(
            project_name=project_name,
            output_dir=output_dir,
            namespace=namespace
        )
        generator.generate_artifacts(model, cds_gen=cds_gen, tudf=tudf, archive=archive)
        return "CAP artifacts generated successfully. Root directory: " + str(Path(os.path.join(generator.output_dir, generator.project_name)).as_posix())

    async def _run_async(
        self, name: str, version: str, project_name: str, output_dir: str, namespace: Optional[str] = None,
        cds_gen: Optional[bool] = False, tudf: Optional[bool] = False, archive: Optional[bool] = False,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        return self._run(name, version, project_name, output_dir, namespace, cds_gen, tudf, archive, run_manager)



class CAPArtifactsForBASTool(BaseTool):
    """
    This tool generates CAP artifacts for a given model.

    Parameters
    ----------
    connection_context : ConnectionContext
        Connection context to the HANA database.

    Returns
    -------
    str
        The directory to the generated CAP artifacts.

        .. note::

            args_schema is used to define the schema of the inputs as follows:

            .. list-table::
                :widths: 15 50
                :header-rows: 1

                * - Field
                  - Description
                * - name
                  - The name of the model in model storage. If not provided, ask the user. Do not guess.
                * - version
                  - The version of the model in model storage. If not provided, ask the user. Do not guess.
                * - cds_gen
                  - Whether to generate CDS files for CAP project, it is optional.
                * - tudf
                  - Whether to generate table UDF for CAP project, it is optional.
                * - archive
                  - Whether to archive the generated artifacts, it is optional.
    """
    name: str = "cap_artifacts_for_bas"
    """Name of the tool."""
    description: str = "To generate CAP artifacts for a given model from model storage. "
    """Description of the tool."""
    connection_context: ConnectionContext = None
    """Connection context to the HANA database."""
    args_schema: Type[BaseModel] = CAPArtifactsForBASInput
    return_direct: bool = False

    def __init__(
        self,
        connection_context: ConnectionContext,
        return_direct: bool = False
    ) -> None:
        super().__init__(  # type: ignore[call-arg]
            connection_context=connection_context,
            return_direct=return_direct
        )

    def _run(
        self, name: str, version: str,
        cds_gen: Optional[bool] = False, tudf: Optional[bool] = False, archive: Optional[bool] = True,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        ms = ModelStorage(connection_context=self.connection_context)
        model = ms.load_model(name, version)
        # if archive is None:
        #     archive = True
        temp_root = Path(tempfile.gettempdir())
        output_dir = os.path.join(temp_root, "hana-ai")
        os.makedirs(output_dir, exist_ok=True)
        generator = HANAGeneratorForCAP(
            project_name="capproject",
            output_dir=output_dir
        )
        generator.generate_artifacts(model, cds_gen=cds_gen, tudf=tudf, archive=archive)
        return json.dumps({"generated_cap_project" : str(Path(os.path.join(generator.output_dir, generator.project_name)).as_posix())})

    async def _run_async(
        self, name: str, version: str, project_name: str, output_dir: str, namespace: Optional[str] = None,
        cds_gen: Optional[bool] = False, tudf: Optional[bool] = False, archive: Optional[bool] = True,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        return self._run(name, version, project_name, output_dir, namespace, cds_gen, tudf, archive, run_manager)
