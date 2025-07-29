"""
Test building stages DAG.
"""

from collections.abc import Callable
from typing import Union

from cpg_flow.stage import (
    CohortStage,
    DatasetStage,
    MultiCohortStage,
    SequencingGroupStage,
    StageDecorator,
    StageInput,
    StageOutput,
    stage,
)
from cpg_flow.targets import Cohort, Dataset, MultiCohort, SequencingGroup
from cpg_flow.workflow import (
    run_workflow as _run_workflow,
)
from cpg_utils import Path, to_path
from cpg_utils.config import dataset_path
from cpg_utils.hail_batch import get_batch


def add_sg(ds, id, external_id: str) -> SequencingGroup:
    sg = ds.add_sequencing_group(
        id=id,
        external_id=external_id,
        sequencing_type='genome',
        sequencing_technology='short-read',
        sequencing_platform='illumina',
    )
    return sg


def mock_cohort() -> MultiCohort:
    m = MultiCohort()
    c = m.create_cohort(id='COH123', name='fewgenomes', dataset='fewgenomes')
    d = m.create_dataset('my_dataset')

    sg1 = add_sg(d, 'CPGAA', external_id='SAMPLE1')
    c.add_sequencing_group_object(sg1)
    return m


def mock_multidataset_cohort() -> MultiCohort:
    m = MultiCohort()
    c = m.create_cohort(id='COH123', name='fewgenomes', dataset='fewgenomes')

    ds = m.create_dataset('my_dataset')

    sg1 = add_sg(ds, 'CPGAA', external_id='SAMPLE1')
    sg2 = add_sg(ds, 'CPGBB', external_id='SAMPLE2')

    c.add_sequencing_group_object(sg1)
    c.add_sequencing_group_object(sg2)

    ds2 = m.create_dataset('my_dataset2')

    sg3 = add_sg(ds2, 'CPGCC', external_id='SAMPLE3')
    sg4 = add_sg(ds2, 'CPGDD', external_id='SAMPLE4')
    c.add_sequencing_group_object(sg3)
    c.add_sequencing_group_object(sg4)

    return m


def mock_multicohort() -> MultiCohort:
    mc = MultiCohort()

    # Create a cohort with two datasets
    cohort_a = mc.create_cohort(id='COH111', name='CohortA', dataset='projecta')
    # Create a dataset in the cohort (legacy)
    ds = mc.create_dataset('projecta')

    # Add sequencing groups to the cohort AND dataset
    cohort_a.add_sequencing_group_object(add_sg(ds, 'CPGXXXX', external_id='SAMPLE1'))
    cohort_a.add_sequencing_group_object(add_sg(ds, 'CPGAAAA', external_id='SAMPLE2'))

    # same cohort, samples from a second Dataset
    ds2 = mc.create_dataset('projectc')
    cohort_a.add_sequencing_group_object(add_sg(ds2, 'CPGCCCC', external_id='SAMPLE3'))
    cohort_a.add_sequencing_group_object(add_sg(ds2, 'CPGDDDD', external_id='SAMPLE4'))

    # second cohort, third dataset
    cohort_b = mc.create_cohort(id='COH222', name='CohortB', dataset='projectb')
    ds3 = mc.create_dataset('projectb')
    cohort_b.add_sequencing_group_object(add_sg(ds3, 'CPGEEEEEE', external_id='SAMPLE5'))
    cohort_b.add_sequencing_group_object(add_sg(ds3, 'CPGFFFFFF', external_id='SAMPLE6'))

    return mc


class TestStage(SequencingGroupStage):
    def expected_outputs(self, sequencing_group: SequencingGroup) -> Path:
        return to_path(dataset_path(f'{sequencing_group.id}_{self.name}.tsv'))

    def queue_jobs(self, sequencing_group: SequencingGroup, inputs: StageInput) -> StageOutput | None:
        j = get_batch().new_job(self.name, attributes=self.get_job_attrs(sequencing_group))
        return self.make_outputs(sequencing_group, self.expected_outputs(sequencing_group), jobs=j)


class TestDatasetStage(DatasetStage):
    def expected_outputs(self, dataset: Dataset) -> Path:
        return to_path(dataset_path(f'{dataset.name}_{self.name}.tsv'))

    def queue_jobs(self, dataset: Dataset, inputs: StageInput) -> StageOutput | None:
        j = get_batch().new_job(self.name, attributes=self.get_job_attrs(dataset))
        return self.make_outputs(dataset, self.expected_outputs(dataset), jobs=j)


class TestCohortStage(CohortStage):
    def expected_outputs(self, cohort: Cohort) -> Path:
        return to_path(dataset_path(f'{cohort.name}_{self.name}.tsv'))

    def queue_jobs(self, cohort: Cohort, inputs: StageInput) -> StageOutput | None:
        j = get_batch().new_job(self.name, attributes=self.get_job_attrs(cohort))
        return self.make_outputs(cohort, self.expected_outputs(cohort), jobs=j)


class TestMultiCohortStage(MultiCohortStage):
    def expected_outputs(self, multicohort: MultiCohort) -> Path:
        return to_path(dataset_path(f'{multicohort.name}_{self.name}.tsv'))

    def queue_jobs(self, multicohort: MultiCohort, inputs: StageInput) -> StageOutput | None:
        j = get_batch().new_job(self.name, attributes=self.get_job_attrs(multicohort))
        return self.make_outputs(multicohort, self.expected_outputs(multicohort), jobs=j)


# A -> B -> C -> D
@stage
class A(TestStage):
    pass


@stage(required_stages=A)
class B(TestStage):
    pass


@stage(required_stages=B)
class C(TestStage):
    pass


@stage(required_stages=C)
class D(TestStage):
    pass


# A2 -> B2 -> C2
@stage
class A2(TestStage):
    pass


@stage(required_stages=A2)
class B2(TestStage):
    pass


@stage(required_stages=B2)
class C2(TestStage):
    pass


@stage()
class SGStage1(TestStage):
    pass


@stage()
class DatasetStage1(TestDatasetStage):
    pass


@stage()
class DatasetStage2(TestDatasetStage):
    pass


@stage()
class CohortStage1(TestCohortStage):
    pass


@stage()
class MultiCohortStage1(TestMultiCohortStage):
    pass


StageType = Union[type[TestStage], type[TestDatasetStage], type[TestCohortStage], type[TestMultiCohortStage]]


def run_workflow(
    mocker,
    cohort_mocker: Callable[..., Cohort | MultiCohort] = mock_cohort,
    stages: list[StageDecorator] | None = None,
):
    mocker.patch('cpg_flow.inputs.create_multicohort', lambda x: cohort_mocker())
    mocker.patch('cpg_flow.inputs.get_multicohort', cohort_mocker)

    stages = stages or [C, C2]
    _run_workflow(stages)
