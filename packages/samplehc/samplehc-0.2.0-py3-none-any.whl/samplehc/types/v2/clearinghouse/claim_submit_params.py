# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = [
    "ClaimSubmitParams",
    "Input",
    "InputClaimInformation",
    "InputClaimInformationClaimCodeInformation",
    "InputClaimInformationClaimDateInformation",
    "InputClaimInformationPrincipalDiagnosis",
    "InputClaimInformationServiceLine",
    "InputClaimInformationServiceLineInstitutionalService",
    "InputProvider",
    "InputProviderContactInformation",
    "InputProviderAddress",
    "InputReceiver",
    "InputSubmitter",
    "InputSubmitterContactInformation",
    "InputSubscriber",
]


class ClaimSubmitParams(TypedDict, total=False):
    input: Required[Input]


class InputClaimInformationClaimCodeInformation(TypedDict, total=False):
    admission_source_code: Required[Annotated[str, PropertyInfo(alias="admissionSourceCode")]]

    admission_type_code: Required[Annotated[str, PropertyInfo(alias="admissionTypeCode")]]

    patient_status_code: Required[Annotated[str, PropertyInfo(alias="patientStatusCode")]]


class InputClaimInformationClaimDateInformation(TypedDict, total=False):
    admission_date_and_hour: Required[Annotated[str, PropertyInfo(alias="admissionDateAndHour")]]

    statement_begin_date: Required[Annotated[str, PropertyInfo(alias="statementBeginDate")]]

    statement_end_date: Required[Annotated[str, PropertyInfo(alias="statementEndDate")]]


class InputClaimInformationPrincipalDiagnosis(TypedDict, total=False):
    principal_diagnosis_code: Required[Annotated[str, PropertyInfo(alias="principalDiagnosisCode")]]

    qualifier_code: Annotated[str, PropertyInfo(alias="qualifierCode")]


class InputClaimInformationServiceLineInstitutionalService(TypedDict, total=False):
    line_item_charge_amount: Required[Annotated[str, PropertyInfo(alias="lineItemChargeAmount")]]

    procedure_code: Required[Annotated[str, PropertyInfo(alias="procedureCode")]]

    service_line_revenue_code: Required[Annotated[str, PropertyInfo(alias="serviceLineRevenueCode")]]

    measurement_unit: Annotated[str, PropertyInfo(alias="measurementUnit")]

    procedure_identifier: Annotated[str, PropertyInfo(alias="procedureIdentifier")]

    service_unit_count: Annotated[str, PropertyInfo(alias="serviceUnitCount")]


class InputClaimInformationServiceLine(TypedDict, total=False):
    institutional_service: Required[
        Annotated[InputClaimInformationServiceLineInstitutionalService, PropertyInfo(alias="institutionalService")]
    ]

    line_item_control_number: Required[Annotated[str, PropertyInfo(alias="lineItemControlNumber")]]

    service_date: Required[Annotated[str, PropertyInfo(alias="serviceDate")]]

    service_date_end: Annotated[str, PropertyInfo(alias="serviceDateEnd")]


class InputClaimInformation(TypedDict, total=False):
    benefits_assignment_certification_indicator: Required[
        Annotated[str, PropertyInfo(alias="benefitsAssignmentCertificationIndicator")]
    ]

    claim_charge_amount: Required[Annotated[str, PropertyInfo(alias="claimChargeAmount")]]

    claim_code_information: Required[
        Annotated[InputClaimInformationClaimCodeInformation, PropertyInfo(alias="claimCodeInformation")]
    ]

    claim_date_information: Required[
        Annotated[InputClaimInformationClaimDateInformation, PropertyInfo(alias="claimDateInformation")]
    ]

    claim_filing_code: Required[Annotated[str, PropertyInfo(alias="claimFilingCode")]]

    claim_frequency_code: Required[Annotated[str, PropertyInfo(alias="claimFrequencyCode")]]

    patient_control_number: Required[Annotated[str, PropertyInfo(alias="patientControlNumber")]]

    place_of_service_code: Required[Annotated[str, PropertyInfo(alias="placeOfServiceCode")]]

    plan_participation_code: Required[Annotated[str, PropertyInfo(alias="planParticipationCode")]]

    principal_diagnosis: Required[
        Annotated[InputClaimInformationPrincipalDiagnosis, PropertyInfo(alias="principalDiagnosis")]
    ]

    release_information_code: Required[Annotated[str, PropertyInfo(alias="releaseInformationCode")]]

    service_lines: Required[Annotated[Iterable[InputClaimInformationServiceLine], PropertyInfo(alias="serviceLines")]]


class InputProviderContactInformation(TypedDict, total=False):
    name: Required[str]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]


class InputProviderAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    postal_code: Required[Annotated[str, PropertyInfo(alias="postalCode")]]

    state: Required[str]


class InputProvider(TypedDict, total=False):
    contact_information: Required[Annotated[InputProviderContactInformation, PropertyInfo(alias="contactInformation")]]

    npi: Required[str]

    provider_type: Required[Annotated[str, PropertyInfo(alias="providerType")]]

    address: InputProviderAddress

    employer_id: Annotated[str, PropertyInfo(alias="employerId")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]


class InputReceiver(TypedDict, total=False):
    organization_name: Required[Annotated[str, PropertyInfo(alias="organizationName")]]


class InputSubmitterContactInformation(TypedDict, total=False):
    name: Required[str]

    phone_number: Required[Annotated[str, PropertyInfo(alias="phoneNumber")]]


class InputSubmitter(TypedDict, total=False):
    contact_information: Required[Annotated[InputSubmitterContactInformation, PropertyInfo(alias="contactInformation")]]

    organization_name: Required[Annotated[str, PropertyInfo(alias="organizationName")]]

    tax_id: Required[Annotated[str, PropertyInfo(alias="taxId")]]


class InputSubscriber(TypedDict, total=False):
    first_name: Required[Annotated[str, PropertyInfo(alias="firstName")]]

    group_number: Required[Annotated[str, PropertyInfo(alias="groupNumber")]]

    last_name: Required[Annotated[str, PropertyInfo(alias="lastName")]]

    member_id: Required[Annotated[str, PropertyInfo(alias="memberId")]]

    payment_responsibility_level_code: Required[Annotated[str, PropertyInfo(alias="paymentResponsibilityLevelCode")]]


class Input(TypedDict, total=False):
    claim_information: Required[Annotated[InputClaimInformation, PropertyInfo(alias="claimInformation")]]

    is_testing: Required[Annotated[bool, PropertyInfo(alias="isTesting")]]

    providers: Required[Iterable[InputProvider]]

    receiver: Required[InputReceiver]

    submitter: Required[InputSubmitter]

    subscriber: Required[InputSubscriber]

    trading_partner_name: Required[Annotated[str, PropertyInfo(alias="tradingPartnerName")]]

    trading_partner_service_id: Required[Annotated[str, PropertyInfo(alias="tradingPartnerServiceId")]]
