from typing import Literal, Union

from truefoundry.deploy._autogen import models
from truefoundry.deploy.lib.model.entity import Deployment
from truefoundry.deploy.v2.lib.deploy import deploy_component
from truefoundry.deploy.v2.lib.patched_models import LocalSource
from truefoundry.pydantic_v1 import BaseModel, Field, conint


class DeployablePatchedModelBase(BaseModel):
    class Config:
        extra = "forbid"

    def deploy(
        self, workspace_fqn: str, wait: bool = True, force: bool = False
    ) -> Deployment:
        return deploy_component(
            component=self,
            workspace_fqn=workspace_fqn,
            wait=wait,
            force=force,
        )


class Service(models.Service, DeployablePatchedModelBase):
    type: Literal["service"] = "service"
    resources: models.Resources = Field(default_factory=models.Resources)
    # This is being patched because cue export marks this as a "number"
    replicas: Union[conint(ge=0, le=100), models.ServiceAutoscaling] = Field(  # type: ignore[valid-type]
        1,
        description="+label=Replicas\n+usage=Replicas of service you want to run\n+icon=fa-clone\n+sort=3",
    )


class Job(models.Job, DeployablePatchedModelBase):
    type: Literal["job"] = "job"
    resources: models.Resources = Field(default_factory=models.Resources)


class SparkJob(models.SparkJob, DeployablePatchedModelBase):
    type: Literal["spark-job"] = "spark-job"


class Notebook(models.Notebook, DeployablePatchedModelBase):
    type: Literal["notebook"] = "notebook"
    resources: models.Resources = Field(default_factory=models.Resources)


class Codeserver(models.Codeserver, DeployablePatchedModelBase):
    type: Literal["codeserver"] = "codeserver"
    resources: models.Resources = Field(default_factory=models.Resources)


class RStudio(models.RStudio, DeployablePatchedModelBase):
    type: Literal["rstudio"] = "rstudio"
    resources: models.Resources = Field(default_factory=models.Resources)


class Helm(models.Helm, DeployablePatchedModelBase):
    type: Literal["helm"] = "helm"


class Volume(models.Volume, DeployablePatchedModelBase):
    type: Literal["volume"] = "volume"


class ApplicationSet(models.ApplicationSet, DeployablePatchedModelBase):
    type: Literal["application-set"] = "application-set"


class AsyncService(models.AsyncService, DeployablePatchedModelBase):
    type: Literal["async-service"] = "async-service"
    replicas: Union[conint(ge=0, le=100), models.AsyncServiceAutoscaling] = 1  # type: ignore[valid-type]
    resources: models.Resources = Field(default_factory=models.Resources)


class SSHServer(models.SSHServer, DeployablePatchedModelBase):
    type: Literal["ssh-server"] = "ssh-server"
    resources: models.Resources = Field(default_factory=models.Resources)


class Workflow(models.Workflow, DeployablePatchedModelBase):
    type: Literal["workflow"] = "workflow"
    source: Union[models.RemoteSource, models.LocalSource] = Field(
        default_factory=lambda: LocalSource(local_build=False)
    )

    def deploy(
        self, workspace_fqn: str, wait: bool = True, force: bool = False
    ) -> Deployment:
        from truefoundry.deploy.v2.lib.deploy_workflow import deploy_workflow

        return deploy_workflow(
            workflow=self, workspace_fqn=workspace_fqn, wait=wait, force=force
        )


class Application(models.Application, DeployablePatchedModelBase):
    # We need a discriminator field to the root model to simplify the Validation errors
    # Unfortunately cue export cannot add discriminator in OAS
    # Even if we add it manually in OAS, `datamodel-code-generator` has bugs when discriminator field is enum type in member models.
    # It will change the members to be incorrect like this
    # >>> class Service(BaseModel):
    # >>>     type: Literal["Service"] = Field("Service")  # notice the capital casing
    # This is why we add it manually here
    __root__: Union[
        models.Service,
        models.AsyncService,
        models.Job,
        models.Notebook,
        models.Codeserver,
        models.SSHServer,
        models.RStudio,
        models.Helm,
        models.Volume,
        models.ApplicationSet,
        models.Workflow,
        models.SparkJob,
    ] = Field(..., description="", discriminator="type")

    def deploy(
        self, workspace_fqn: str, wait: bool = True, force: bool = False
    ) -> Deployment:
        if isinstance(self.__root__, models.Workflow):
            from truefoundry.deploy.v2.lib.deploy_workflow import deploy_workflow

            return deploy_workflow(
                workflow=self.__root__,
                workspace_fqn=workspace_fqn,
                wait=wait,
                force=force,
            )
        else:
            return deploy_component(
                component=self.__root__,
                workspace_fqn=workspace_fqn,
                wait=wait,
                force=force,
            )
