# coding: utf-8

"""
    University Card API

     # Card Specification  ## Specification revisions  | Rev. | Author | Date | Comments | | -- | -- | -- | -- | | 1 | C.J.Sendall | 12-Feb-07 | Created | | 2 | C.J.Sendall | 9-Aug-07 | Specify integer format of Mifare Number | | 3 | C.J.Sendall | 12-Jun-15 | Description of UL barcode changed | | 4 | E. Kirk (ek599) | 11-Sep-24 | Refine and consolidate card specification and other documentation. Moved and change format to markdown. |   ### Links to previous revisions  | Rev. | Link | | -- | -- | | 3 | https://docs.google.com/document/d/1WjfD5Ags-mBInKouvnledlShzjvYkq4RQuK7P5hoHPY |   ## Card technology  The University Card Office started using **Mifare classic 4K** cards for the University Card in August 2006. \"Mifare Classic\" defines both hardware requirements and the proprietary protocols used. Further details are available at https://www.mifare.net/ but generally card readers need to be specified to (completely) support \"Mifare Classic\", including the Mifare Classic 4K variant.  ## Read and write keys  In order to read from most fields on the card respective \"read keys\" are needed. If you need access to the read keys (e.g. when installing a new card readers), please contact universitycard-dev@uis.cam.ac.uk and they will be made available via a secure mechanism. The read keys need to be treated like passwords; they must be stored and managed securely and should never be shared with third parties.  Corresponding write keys are needed to write to blocks. These are not generally available outside of the card printing processes.  ## Security  Mifare Classic protocols have known exploits and are no longer considered secure. While the technology is in use, the UIS card team follows sensible security practices (e.g. keeping read keys secured).  ## Card Layout  ### Fields to use  The following fields can be used for the purpose of identifying cards and users for access control purposes. **No other fields are supported for access control purposes.**  | Fields | Location | | -- | -- | | UCam Card ID (historically, mifare number) | Sector 1 Block 2 |  ### Personal and access only cards  The following table indicates which fields are available on the 2 types of cards printed, \"Personal\" and \"Temporary Access Cards\".  | Fields | Personal | Temporary Access Cards | | -- | -- | -- | | (Globaly unique factory) MIFARE ID | x | x | | [DEPRECIATED] Cardholder ID* | x | | | [DEPRECIATED] Issue Number* | x | | | **UCam Card ID** (historically, Mifare Number)* | x | x | | [DEPRECIATED] CRSID | x | | | [DEPRECIATED] USN | x | | | [DEPRECIATED] Staff number | x | | | [DEPRECIATED] Expiry date | x | | | [DEPRECIATED] Issue date | x | | | [DEPRECIATED] UL barcode | x | |  *Fields marked as depreciated should no longer be accessed from the card itself.*  \\* See Endnotes - Card Reader Programming  ### Detailed card format  The card layout table lists all values that are **potentially** present on cards (see Personal and access only cards).  | Sector | Block 0 | Block 1 | Block 2 | Requires Read Keys | MAD | | -- | -- | -- | -- | -- | -- | | 0 | (Globaly unique factory) MIFARE ID | MAD directory | MAD directory | No | - | | 1 | [DEPRECIATED] Cardholder ID | [DEPRECIATED] Issue Number | **UCam Card ID** (historically, Mifare Number) | Yes | 5810 | | 2 | [DEPRECIATED] CRSID | [DEPRECIATED] USN | [DEPRECIATED] Staff number | Yes | 5811 | | 3 | [DEPRECIATED] Expiry date | [DEPRECIATED] Issue date | [DEPRECIATED] UL barcode | Yes | 5812 | | 4 | [DEPRECIATED] Cardholder ID* | [DEPRECIATED] Issue Number* | [LOCATION DEPRECIATED] UCam Card ID | Yes | 5813 | | 5-15 | | | | Yes | 0000 | | 16 | MAD2 directory | | MAD2 directory | No | - | | 17-33 | | | | Yes | 0000 | | 34-39 | | | | Yes | 0002 |   Fields marked as depreciated should no longer be accessed from the card itself. Some fields are available from Card API using the UCam Card ID to query data on users, e.g. to get CRSID.  MIFARE Application Directory (MAD) entries of 5810,5811,5812,5813 are Application Identifiers (AIDs). A MAD entry of  0002 means reserved and 0000 means free.  ### Data Specification  All sectors padded with trailing nulls or blanks  | Name | Charset | Length | Description | | -- | -- | -- | -- | | [DEPRECIATED] Cardholder ID | ASCII | 7 characters | two lower case letters, four digits , lower case  letter (checksum) | | [DEPRECIATED] Issue Number | ASCII | 2 digits | | | **UCam Card ID** (historically, Mifare Number) | integer | 32bits | Up to 8 digit integer (little-endian,  i.e. the least significant byte comes first) | | [DEPRECIATED] CRSID | ASCII | 4-7 characters | Upper case letters and digits | | [DEPRECIATED] USN | ASCII | 9 digits | | | [DEPRECIATED] Staff number | Up to 6 digits | | | [DEPRECIATED] Expiry date | ASCII | 10 | yyyy/mm/dd | | [DEPRECIATED] Issue date | ASCII | 10 | yyyy/mm/dd | | [DEPRECIATED] UL barcode | ASCII | 5 characters | 5 upper case letters and digits, starting with V |  ## Endnotes  ### Card Reader Programming It has been witnessed that some card readers have likely been programmed to calculate the UCam Card ID from the depreciated Cardholder ID and Issue Number. When personal cards are printed, they currently generate the UCam Card ID from the depreciated fields Cardholder ID and Issue Number using a legacy algorithm. Affected readers appear to use the same algorithm to generate or validate the UCam Card ID from these depreciated fields. It is unknown by the current team operating the card system why some readers were programmed in such a way. Temporary access cards printed since 2021 do not have the depreciated fields Cardholder ID and Issue Number and generate the UCam Card ID value differently. *Card readers that are not just using the UCam Card ID should be reprogrammed or replaced.*    # Card API  ## Introduction  The Card API allows access to information about University Cards.  The API broadly follows the principles of REST and strives to provide an interface that can be easily consumed by downstream systems.  ### Stability  This release of the Card API is a `beta` offering: a service we are moving towards live but which requires wider testing with a broader group of users. We consider the Card API as being at least as stable as the legacy card system which it aims to replace, so we encourage users to make use of the Card API rather than relying on the legacy card system.  ### Versioning  The Card API is versioned using url path prefixes in the format: `/v1beta1/cards`. This follows the pattern established by the [GCP API](https://cloud.google.com/apis/design/versioning). Breaking changes will not be made without a change in API major version, however non-breaking changes will be introduced without changes to the version path prefix. All changes will be documented in the project's [CHANGELOG](https://gitlab.developers.cam.ac.uk/uis/devops/iam/card-database/card-api/-/blob/master/CHANGELOG.md).  The available versions of the API are listed at the API's root.  ### Domain  The Card API has been designed to only expose information about University Cards and the identifiers which link a Card to a person. The API does not expose information about cardholders or the institutions that a cardholder belongs to. This is in order to combat domain crossover and to ensure the Card API does not duplicate information which is held and managed within systems such as Lookup, CamSIS or CHRIS.  It is expected that the Card API should be used alongside APIs such as Lookup which allow personal and institutional membership information to be retrieved. A tool has been written in order to allow efficient querying of the Card API using information contained within, CamSIS or CHRIS. [Usage and installation instructions for this tool can be found here](https://gitlab.developers.cam.ac.uk/uis/devops/iam/card-database/card-client).  ### Data source  The data exposed in the Card API is currently a mirror of data contained within the [Card Database](https://webservices.admin.cam.ac.uk/uc/). With data being synced from the Card Database to the Card API hourly.  In future, card data will be updated and created directly using the Card API so changes will be reflected in the Card API 'live' without this hourly sync.  ## Core entities  ### The `Card` Entity  The `Card` entity is a representation of a physical University Card. The entity contains fields indicating the status of the card and when the card has moved between different statuses. Cards held by individuals (such as students or staff) and temporary cards managed by institutions are both represented by the `Card` entity, with the former having a `cardType` of `MIFARE_PERSONAL` and the latter having a `cardType` of `MIFARE_TEMPORARY`.  Each card should have a set of `CardIdentifiers` which allow the card to be linked to an entity in another system (e.g. a person in Lookup), or record information about identifiers held within the card, such as Mifare ID.  The full `Card` entity contains a `cardNotes` field which holds a set of notes made by administrator users related to the card, as well as an `attributes` field which holds the data that is present on the physical presentation of a card. Operations which list many cards return `CardSummary` entities which omit these fields for brevity.  ### The `CardIdentifier` Entity  The `CardIdentifier` entity holds the `value` and `scheme` of a given identifier. The `value` field of a `CardIdentifier` is a simple ID string - e.g. `wgd23` or `000001`. The `scheme` field of a `CardIdentifier` indicates what system this identifier relates to or was issued by. This allows many identifiers which relate to different systems to be recorded against a single `Card`.  > **WARNING!** > > A barcode identifier (`barcode.v1.card.university.identifiers.cam.ac.uk`) may be associated with more than one user. See `Known Issues` for more details.  The supported schemes are: * `v1.person.identifiers.cam.ac.uk`: The CRSid of the person who holds this card * `person.v1.student-records.university.identifiers.cam.ac.uk`: The CamSIS identifier (USN) of the person who holds this card * `person.v1.human-resources.university.identifiers.cam.ac.uk`: The CHRIS identifier (staff number) of the person who holds this card * `person.v1.board-of-graduate-studies.university.identifiers.cam.ac.uk`: The Board of Graduate Studies identifier of the person who holds this card * `person.v1.legacy-card.university.identifiers.cam.ac.uk`: The legacy card holder ID for the person who holds this card * `mifare-identifier.v1.card.university.identifiers.cam.ac.uk`: The Mifare ID which is embedded in this card (this     identifier uniquely identifies a single card) * `mifare-number.v1.card.university.identifiers.cam.ac.uk`: The Mifare Number which is embedded in this card     (this identifier is a digest of card's legacy cardholder ID and issue number, so is not     guaranteed to be unique) * `card.v1.legacy-card.university.identifiers.cam.ac.uk`: The legacy card ID from the card database * `temporary-card.v1.card.university.identifiers.cam.ac.uk`: The temporary card ID from the card database * `photo.v1.photo.university.identifiers.cam.ac.uk`: The ID of the photo printed on this card * `barcode.v1.card.university.identifiers.cam.ac.uk`: The barcode printed on this card * `institution.v1.legacy-card.university.identifiers.cam.ac.uk`: The legacy institution ID from the card database (only populated on temporary cards)   ## Using the API  ### Auth  To authenticate against the Card API, an application must be registered within the API Service, the application must be owned by a team account as opposed to an individual account and the application must be granted access to the `University Card` product. Details of how to register an application and grant access to products can be found in the [API Service Getting Started Guide](https://developer.api.apps.cam.ac.uk/start-using-an-api).  #### Principal  Throughout this specification the term `principal` is used to describe the user or service who is making use of the API. When authenticating using the OAuth2 client credentials flow the principal shall be the application registered within the API Gateway. When authenticating using the authorization code flow, e.g. via a Single Page Application, the principal shall be the user who has authenticated and consented to give the application access to the data contained within this API - identified by their CRSid.  This specification references permissions which can be granted to any principal - please contact the API maintainers to grant a principal a specific permission.  ### Content Type  The Card API responds with JSON data. The `Content-Type` request header should be omitted or set to `application/json`. If an invalid `Content-Type` header is sent the API will respond with `415 Unsupported Media Type`.  ### Pagination  For all operations where multiple entities will be returned, the API will return a paginated result. This is to account for too many entities needing to be returned within a single response. A Paginated response has the structure:  ```json {   \"next\": \"https://<gateway_host>/card/v1beta1/cards/?cursor=cD0yMDIxLTAxL   \"previous\": null,   \"results\": [       ... the data for the current page   ] }  ```  The `next` field holds the url of the next page of results, containing a cursor which indicates to the API which page of results to return. If the `next` field is `null` no further results are available. The `previous` field can be used to navigate backwards through pages of results.  The `page_size` query parameter can be used to control the number of results to return. This defaults to 200 but can be set to a maximum of 500, if set to greater than this no error will be returned but only 500 results will be given in the response.  ## Known Issues  ### Barcodes  There are barcodes in the Card API that are associated with multiple users. The two main causes of this are:   - imported records from the previous card system   - a bug that existed in the current system were the same barcode is assigned to multiple users     created at the same time  The Card API service team are working towards no active cards (status=ISSUED) sharing the same barcode. Defences have been put it place to prevent new duplicate barcodes occurring.  **Clients of the Card API should expect expired cards and card requests to potentially be associated with a barcode that is also associated with cards and card requests of a different user. As the `card-identifiers` endpoint uses all cards/card requests to link identifiers, when looking up using effected barcodes, multiple users (via identifiers) will always remain associated.**  The `discontinued-identifiers` endpoint provides details of identifiers that are no longer to be **reused**. Records in `discontinued-identifiers` prevent reusing the specified identifier with **new** card requests. This endpoint can be queried for barcodes that have been identified as being associated with multiple users.  

    The version of the OpenAPI document: v1beta1
    Contact: universitycard-dev@uis.cam.ac.uk
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501

import warnings
from pydantic import validate_call, Field, StrictFloat, StrictStr, StrictInt
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated

from datetime import datetime
from pydantic import Field, StrictBool, StrictBytes, StrictInt, StrictStr, field_validator
from typing import List, Optional, Union
from typing_extensions import Annotated
from identitylib.card_client.models.available_barcode import AvailableBarcode
from identitylib.card_client.models.available_barcode_batch_request import AvailableBarcodeBatchRequest
from identitylib.card_client.models.available_barcode_batch_response_type import AvailableBarcodeBatchResponseType
from identitylib.card_client.models.available_barcode_request import AvailableBarcodeRequest
from identitylib.card_client.models.card import Card
from identitylib.card_client.models.card_bulk_update_request import CardBulkUpdateRequest
from identitylib.card_client.models.card_bulk_update_response_type import CardBulkUpdateResponseType
from identitylib.card_client.models.card_filter_request import CardFilterRequest
from identitylib.card_client.models.card_identifier import CardIdentifier
from identitylib.card_client.models.card_identifier_bulk_update_request import CardIdentifierBulkUpdateRequest
from identitylib.card_client.models.card_identifier_bulk_update_response_type import CardIdentifierBulkUpdateResponseType
from identitylib.card_client.models.card_identifier_destroy_response_type import CardIdentifierDestroyResponseType
from identitylib.card_client.models.card_identifier_update_request import CardIdentifierUpdateRequest
from identitylib.card_client.models.card_identifier_update_response_type import CardIdentifierUpdateResponseType
from identitylib.card_client.models.card_logo import CardLogo
from identitylib.card_client.models.card_note import CardNote
from identitylib.card_client.models.card_note_create_request_type_request import CardNoteCreateRequestTypeRequest
from identitylib.card_client.models.card_note_destroy_response_type import CardNoteDestroyResponseType
from identitylib.card_client.models.card_rfid_config_list_response_type import CardRFIDConfigListResponseType
from identitylib.card_client.models.card_request import CardRequest
from identitylib.card_client.models.card_request_bulk_update_request import CardRequestBulkUpdateRequest
from identitylib.card_client.models.card_request_bulk_update_response_type import CardRequestBulkUpdateResponseType
from identitylib.card_client.models.card_request_create_type_request import CardRequestCreateTypeRequest
from identitylib.card_client.models.card_request_distinct_values import CardRequestDistinctValues
from identitylib.card_client.models.card_request_update_request import CardRequestUpdateRequest
from identitylib.card_client.models.card_request_update_response_type import CardRequestUpdateResponseType
from identitylib.card_client.models.card_update_request import CardUpdateRequest
from identitylib.card_client.models.card_update_response_type import CardUpdateResponseType
from identitylib.card_client.models.college_instituions_ids_list_response_type import CollegeInstituionsIdsListResponseType
from identitylib.card_client.models.discontinued_identifier import DiscontinuedIdentifier
from identitylib.card_client.models.discontinued_identifier_create_request import DiscontinuedIdentifierCreateRequest
from identitylib.card_client.models.metrics_list_response_type_wrapper import MetricsListResponseTypeWrapper
from identitylib.card_client.models.paginated_available_barcode_list import PaginatedAvailableBarcodeList
from identitylib.card_client.models.paginated_card_identifier_summary_list import PaginatedCardIdentifierSummaryList
from identitylib.card_client.models.paginated_card_logo_list import PaginatedCardLogoList
from identitylib.card_client.models.paginated_card_note_list import PaginatedCardNoteList
from identitylib.card_client.models.paginated_card_request_summary_list import PaginatedCardRequestSummaryList
from identitylib.card_client.models.paginated_card_summary_list import PaginatedCardSummaryList
from identitylib.card_client.models.paginated_discontinued_identifier_list import PaginatedDiscontinuedIdentifierList

from identitylib.card_client.api_client import ApiClient, RequestSerialized
from identitylib.card_client.api_response import ApiResponse
from identitylib.card_client.rest import RESTResponseType


class V1beta1Api:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def v1beta1_analytics_get(
        self,
        group_by: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> MetricsListResponseTypeWrapper:
        """Get card analytics

         ## Get card analytics  Return a summary of the card system analytics generated from data collected since the legacy system was deprecated, approx. since April 2022.  ### Permissions  Principals with the `CARD_ANALYTICS_READER` permission will be able to affect this endpoint.  

        :param group_by:
        :type group_by: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_analytics_get_serialize(
            group_by=group_by,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "MetricsListResponseTypeWrapper",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_analytics_get_with_http_info(
        self,
        group_by: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[MetricsListResponseTypeWrapper]:
        """Get card analytics

         ## Get card analytics  Return a summary of the card system analytics generated from data collected since the legacy system was deprecated, approx. since April 2022.  ### Permissions  Principals with the `CARD_ANALYTICS_READER` permission will be able to affect this endpoint.  

        :param group_by:
        :type group_by: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_analytics_get_serialize(
            group_by=group_by,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "MetricsListResponseTypeWrapper",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_analytics_get_without_preload_content(
        self,
        group_by: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get card analytics

         ## Get card analytics  Return a summary of the card system analytics generated from data collected since the legacy system was deprecated, approx. since April 2022.  ### Permissions  Principals with the `CARD_ANALYTICS_READER` permission will be able to affect this endpoint.  

        :param group_by:
        :type group_by: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_analytics_get_serialize(
            group_by=group_by,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "MetricsListResponseTypeWrapper",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_analytics_get_serialize(
        self,
        group_by,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if group_by is not None:
            
            _query_params.append(('group_by', group_by))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/analytics',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_available_barcodes_batch_create(
        self,
        available_barcode_batch_request: AvailableBarcodeBatchRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> AvailableBarcodeBatchResponseType:
        """Create multiple available barcodes

         ## Create multiple available barcode in a batch  This method allows the client to create multiple available barcode at once. The response includes the details on which barcodes were created and which already exist.  ### Permissions  Only Principals with the `CARD_REQUEST_UPDATER` permission will be able to create available barcodes.  

        :param available_barcode_batch_request: (required)
        :type available_barcode_batch_request: AvailableBarcodeBatchRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_available_barcodes_batch_create_serialize(
            available_barcode_batch_request=available_barcode_batch_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "AvailableBarcodeBatchResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_available_barcodes_batch_create_with_http_info(
        self,
        available_barcode_batch_request: AvailableBarcodeBatchRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[AvailableBarcodeBatchResponseType]:
        """Create multiple available barcodes

         ## Create multiple available barcode in a batch  This method allows the client to create multiple available barcode at once. The response includes the details on which barcodes were created and which already exist.  ### Permissions  Only Principals with the `CARD_REQUEST_UPDATER` permission will be able to create available barcodes.  

        :param available_barcode_batch_request: (required)
        :type available_barcode_batch_request: AvailableBarcodeBatchRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_available_barcodes_batch_create_serialize(
            available_barcode_batch_request=available_barcode_batch_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "AvailableBarcodeBatchResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_available_barcodes_batch_create_without_preload_content(
        self,
        available_barcode_batch_request: AvailableBarcodeBatchRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Create multiple available barcodes

         ## Create multiple available barcode in a batch  This method allows the client to create multiple available barcode at once. The response includes the details on which barcodes were created and which already exist.  ### Permissions  Only Principals with the `CARD_REQUEST_UPDATER` permission will be able to create available barcodes.  

        :param available_barcode_batch_request: (required)
        :type available_barcode_batch_request: AvailableBarcodeBatchRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_available_barcodes_batch_create_serialize(
            available_barcode_batch_request=available_barcode_batch_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "AvailableBarcodeBatchResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_available_barcodes_batch_create_serialize(
        self,
        available_barcode_batch_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if available_barcode_batch_request is not None:
            _body_params = available_barcode_batch_request


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json', 
                        'application/x-www-form-urlencoded', 
                        'multipart/form-data'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/v1beta1/available-barcodes/batch',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_available_barcodes_create(
        self,
        available_barcode_request: AvailableBarcodeRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> AvailableBarcode:
        """Creates a single available barcode

         ## Create an available barcode  This method allows the client to create a single available barcode. Typically, the batch creation endpoint would be used to import a batch of barcodes all at once, rather than multiple calls to this endpoint.  ### Permissions  Only Principals with the `CARD_REQUEST_UPDATER` permission will be able to create available barcodes.  

        :param available_barcode_request: (required)
        :type available_barcode_request: AvailableBarcodeRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_available_barcodes_create_serialize(
            available_barcode_request=available_barcode_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '201': "AvailableBarcode",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_available_barcodes_create_with_http_info(
        self,
        available_barcode_request: AvailableBarcodeRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[AvailableBarcode]:
        """Creates a single available barcode

         ## Create an available barcode  This method allows the client to create a single available barcode. Typically, the batch creation endpoint would be used to import a batch of barcodes all at once, rather than multiple calls to this endpoint.  ### Permissions  Only Principals with the `CARD_REQUEST_UPDATER` permission will be able to create available barcodes.  

        :param available_barcode_request: (required)
        :type available_barcode_request: AvailableBarcodeRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_available_barcodes_create_serialize(
            available_barcode_request=available_barcode_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '201': "AvailableBarcode",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_available_barcodes_create_without_preload_content(
        self,
        available_barcode_request: AvailableBarcodeRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Creates a single available barcode

         ## Create an available barcode  This method allows the client to create a single available barcode. Typically, the batch creation endpoint would be used to import a batch of barcodes all at once, rather than multiple calls to this endpoint.  ### Permissions  Only Principals with the `CARD_REQUEST_UPDATER` permission will be able to create available barcodes.  

        :param available_barcode_request: (required)
        :type available_barcode_request: AvailableBarcodeRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_available_barcodes_create_serialize(
            available_barcode_request=available_barcode_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '201': "AvailableBarcode",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_available_barcodes_create_serialize(
        self,
        available_barcode_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if available_barcode_request is not None:
            _body_params = available_barcode_request


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json', 
                        'application/x-www-form-urlencoded', 
                        'multipart/form-data'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/v1beta1/available-barcodes',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_available_barcodes_list(
        self,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> PaginatedAvailableBarcodeList:
        """List available barcodes

         ## List Available Barcodes  Returns a list of barcodes which are available to be used by a new University Card.  ### Permissions  Only principals with the `CARD_DATA_READERS` permission are able to list available barcodes.  

        :param cursor: The pagination cursor value.
        :type cursor: str
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_available_barcodes_list_serialize(
            cursor=cursor,
            page_size=page_size,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedAvailableBarcodeList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_available_barcodes_list_with_http_info(
        self,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[PaginatedAvailableBarcodeList]:
        """List available barcodes

         ## List Available Barcodes  Returns a list of barcodes which are available to be used by a new University Card.  ### Permissions  Only principals with the `CARD_DATA_READERS` permission are able to list available barcodes.  

        :param cursor: The pagination cursor value.
        :type cursor: str
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_available_barcodes_list_serialize(
            cursor=cursor,
            page_size=page_size,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedAvailableBarcodeList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_available_barcodes_list_without_preload_content(
        self,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """List available barcodes

         ## List Available Barcodes  Returns a list of barcodes which are available to be used by a new University Card.  ### Permissions  Only principals with the `CARD_DATA_READERS` permission are able to list available barcodes.  

        :param cursor: The pagination cursor value.
        :type cursor: str
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_available_barcodes_list_serialize(
            cursor=cursor,
            page_size=page_size,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedAvailableBarcodeList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_available_barcodes_list_serialize(
        self,
        cursor,
        page_size,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if cursor is not None:
            
            _query_params.append(('cursor', cursor))
            
        if page_size is not None:
            
            _query_params.append(('page_size', page_size))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/available-barcodes',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_available_barcodes_retrieve(
        self,
        barcode: Annotated[StrictStr, Field(description="A unique value identifying this available barcode.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> AvailableBarcode:
        """Get available barcode detail

        Returns a single Available Barcode by ID

        :param barcode: A unique value identifying this available barcode. (required)
        :type barcode: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_available_barcodes_retrieve_serialize(
            barcode=barcode,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "AvailableBarcode",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_available_barcodes_retrieve_with_http_info(
        self,
        barcode: Annotated[StrictStr, Field(description="A unique value identifying this available barcode.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[AvailableBarcode]:
        """Get available barcode detail

        Returns a single Available Barcode by ID

        :param barcode: A unique value identifying this available barcode. (required)
        :type barcode: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_available_barcodes_retrieve_serialize(
            barcode=barcode,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "AvailableBarcode",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_available_barcodes_retrieve_without_preload_content(
        self,
        barcode: Annotated[StrictStr, Field(description="A unique value identifying this available barcode.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get available barcode detail

        Returns a single Available Barcode by ID

        :param barcode: A unique value identifying this available barcode. (required)
        :type barcode: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_available_barcodes_retrieve_serialize(
            barcode=barcode,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "AvailableBarcode",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_available_barcodes_retrieve_serialize(
        self,
        barcode,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if barcode is not None:
            _path_params['barcode'] = barcode
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/available-barcodes/{barcode}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_identifiers_destroy(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card identifier.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CardIdentifierDestroyResponseType:
        """Get card identifier detail

         ## Remove card identifier  This method allows a client to remove a card identifier and in the process delete all associated identifiers, cards, card notes and card requests.  This method only operates on the primary identifiers: - `person.v1.legacy-card.university.identifiers.cam.ac.uk` the CRSid identifier of the cardholder - `person.v1.legacy-card.university.identifiers.cam.ac.uk` the legacy identifier of the cardholder  ### Permissions  Principals with the `CARD_ADMIN` permission are able to affect this endpoint.  

        :param id: A UUID string identifying this card identifier. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_identifiers_destroy_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardIdentifierDestroyResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_identifiers_destroy_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card identifier.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CardIdentifierDestroyResponseType]:
        """Get card identifier detail

         ## Remove card identifier  This method allows a client to remove a card identifier and in the process delete all associated identifiers, cards, card notes and card requests.  This method only operates on the primary identifiers: - `person.v1.legacy-card.university.identifiers.cam.ac.uk` the CRSid identifier of the cardholder - `person.v1.legacy-card.university.identifiers.cam.ac.uk` the legacy identifier of the cardholder  ### Permissions  Principals with the `CARD_ADMIN` permission are able to affect this endpoint.  

        :param id: A UUID string identifying this card identifier. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_identifiers_destroy_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardIdentifierDestroyResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_identifiers_destroy_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card identifier.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get card identifier detail

         ## Remove card identifier  This method allows a client to remove a card identifier and in the process delete all associated identifiers, cards, card notes and card requests.  This method only operates on the primary identifiers: - `person.v1.legacy-card.university.identifiers.cam.ac.uk` the CRSid identifier of the cardholder - `person.v1.legacy-card.university.identifiers.cam.ac.uk` the legacy identifier of the cardholder  ### Permissions  Principals with the `CARD_ADMIN` permission are able to affect this endpoint.  

        :param id: A UUID string identifying this card identifier. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_identifiers_destroy_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardIdentifierDestroyResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_identifiers_destroy_serialize(
        self,
        id,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='DELETE',
            resource_path='/v1beta1/card-identifiers/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_identifiers_list(
        self,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        deleted_at__gte: Optional[datetime] = None,
        deleted_at__isnull: Optional[StrictBool] = None,
        deleted_at__lte: Optional[datetime] = None,
        identifier: Annotated[Optional[StrictStr], Field(description="Email-formatted identifier")] = None,
        is_deleted: Optional[StrictBool] = None,
        is_highest_primary_identifier: Optional[StrictBool] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        retain_until__gte: Optional[datetime] = None,
        retain_until__isnull: Optional[StrictBool] = None,
        retain_until__lte: Optional[datetime] = None,
        scheme: Annotated[Optional[StrictStr], Field(description="Identifier scheme")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> PaginatedCardIdentifierSummaryList:
        """List card identifiers

         ## List card identifiers  Returns a list of card identifiers associated with the cards and card requests.  > **WARNING!** > > A barcode identifier (`barcode.v1.card.university.identifiers.cam.ac.uk`) may be associated with more than one user. See `Known Issues` for more details.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view card identifiers contained within the card system.  

        :param cursor: The pagination cursor value.
        :type cursor: str
        :param deleted_at__gte:
        :type deleted_at__gte: datetime
        :param deleted_at__isnull:
        :type deleted_at__isnull: bool
        :param deleted_at__lte:
        :type deleted_at__lte: datetime
        :param identifier: Email-formatted identifier
        :type identifier: str
        :param is_deleted:
        :type is_deleted: bool
        :param is_highest_primary_identifier:
        :type is_highest_primary_identifier: bool
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param retain_until__gte:
        :type retain_until__gte: datetime
        :param retain_until__isnull:
        :type retain_until__isnull: bool
        :param retain_until__lte:
        :type retain_until__lte: datetime
        :param scheme: Identifier scheme
        :type scheme: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_identifiers_list_serialize(
            cursor=cursor,
            deleted_at__gte=deleted_at__gte,
            deleted_at__isnull=deleted_at__isnull,
            deleted_at__lte=deleted_at__lte,
            identifier=identifier,
            is_deleted=is_deleted,
            is_highest_primary_identifier=is_highest_primary_identifier,
            page_size=page_size,
            retain_until__gte=retain_until__gte,
            retain_until__isnull=retain_until__isnull,
            retain_until__lte=retain_until__lte,
            scheme=scheme,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCardIdentifierSummaryList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_identifiers_list_with_http_info(
        self,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        deleted_at__gte: Optional[datetime] = None,
        deleted_at__isnull: Optional[StrictBool] = None,
        deleted_at__lte: Optional[datetime] = None,
        identifier: Annotated[Optional[StrictStr], Field(description="Email-formatted identifier")] = None,
        is_deleted: Optional[StrictBool] = None,
        is_highest_primary_identifier: Optional[StrictBool] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        retain_until__gte: Optional[datetime] = None,
        retain_until__isnull: Optional[StrictBool] = None,
        retain_until__lte: Optional[datetime] = None,
        scheme: Annotated[Optional[StrictStr], Field(description="Identifier scheme")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[PaginatedCardIdentifierSummaryList]:
        """List card identifiers

         ## List card identifiers  Returns a list of card identifiers associated with the cards and card requests.  > **WARNING!** > > A barcode identifier (`barcode.v1.card.university.identifiers.cam.ac.uk`) may be associated with more than one user. See `Known Issues` for more details.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view card identifiers contained within the card system.  

        :param cursor: The pagination cursor value.
        :type cursor: str
        :param deleted_at__gte:
        :type deleted_at__gte: datetime
        :param deleted_at__isnull:
        :type deleted_at__isnull: bool
        :param deleted_at__lte:
        :type deleted_at__lte: datetime
        :param identifier: Email-formatted identifier
        :type identifier: str
        :param is_deleted:
        :type is_deleted: bool
        :param is_highest_primary_identifier:
        :type is_highest_primary_identifier: bool
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param retain_until__gte:
        :type retain_until__gte: datetime
        :param retain_until__isnull:
        :type retain_until__isnull: bool
        :param retain_until__lte:
        :type retain_until__lte: datetime
        :param scheme: Identifier scheme
        :type scheme: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_identifiers_list_serialize(
            cursor=cursor,
            deleted_at__gte=deleted_at__gte,
            deleted_at__isnull=deleted_at__isnull,
            deleted_at__lte=deleted_at__lte,
            identifier=identifier,
            is_deleted=is_deleted,
            is_highest_primary_identifier=is_highest_primary_identifier,
            page_size=page_size,
            retain_until__gte=retain_until__gte,
            retain_until__isnull=retain_until__isnull,
            retain_until__lte=retain_until__lte,
            scheme=scheme,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCardIdentifierSummaryList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_identifiers_list_without_preload_content(
        self,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        deleted_at__gte: Optional[datetime] = None,
        deleted_at__isnull: Optional[StrictBool] = None,
        deleted_at__lte: Optional[datetime] = None,
        identifier: Annotated[Optional[StrictStr], Field(description="Email-formatted identifier")] = None,
        is_deleted: Optional[StrictBool] = None,
        is_highest_primary_identifier: Optional[StrictBool] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        retain_until__gte: Optional[datetime] = None,
        retain_until__isnull: Optional[StrictBool] = None,
        retain_until__lte: Optional[datetime] = None,
        scheme: Annotated[Optional[StrictStr], Field(description="Identifier scheme")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """List card identifiers

         ## List card identifiers  Returns a list of card identifiers associated with the cards and card requests.  > **WARNING!** > > A barcode identifier (`barcode.v1.card.university.identifiers.cam.ac.uk`) may be associated with more than one user. See `Known Issues` for more details.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view card identifiers contained within the card system.  

        :param cursor: The pagination cursor value.
        :type cursor: str
        :param deleted_at__gte:
        :type deleted_at__gte: datetime
        :param deleted_at__isnull:
        :type deleted_at__isnull: bool
        :param deleted_at__lte:
        :type deleted_at__lte: datetime
        :param identifier: Email-formatted identifier
        :type identifier: str
        :param is_deleted:
        :type is_deleted: bool
        :param is_highest_primary_identifier:
        :type is_highest_primary_identifier: bool
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param retain_until__gte:
        :type retain_until__gte: datetime
        :param retain_until__isnull:
        :type retain_until__isnull: bool
        :param retain_until__lte:
        :type retain_until__lte: datetime
        :param scheme: Identifier scheme
        :type scheme: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_identifiers_list_serialize(
            cursor=cursor,
            deleted_at__gte=deleted_at__gte,
            deleted_at__isnull=deleted_at__isnull,
            deleted_at__lte=deleted_at__lte,
            identifier=identifier,
            is_deleted=is_deleted,
            is_highest_primary_identifier=is_highest_primary_identifier,
            page_size=page_size,
            retain_until__gte=retain_until__gte,
            retain_until__isnull=retain_until__isnull,
            retain_until__lte=retain_until__lte,
            scheme=scheme,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCardIdentifierSummaryList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_identifiers_list_serialize(
        self,
        cursor,
        deleted_at__gte,
        deleted_at__isnull,
        deleted_at__lte,
        identifier,
        is_deleted,
        is_highest_primary_identifier,
        page_size,
        retain_until__gte,
        retain_until__isnull,
        retain_until__lte,
        scheme,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if cursor is not None:
            
            _query_params.append(('cursor', cursor))
            
        if deleted_at__gte is not None:
            if isinstance(deleted_at__gte, datetime):
                _query_params.append(
                    (
                        'deleted_at__gte',
                        deleted_at__gte.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('deleted_at__gte', deleted_at__gte))
            
        if deleted_at__isnull is not None:
            
            _query_params.append(('deleted_at__isnull', deleted_at__isnull))
            
        if deleted_at__lte is not None:
            if isinstance(deleted_at__lte, datetime):
                _query_params.append(
                    (
                        'deleted_at__lte',
                        deleted_at__lte.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('deleted_at__lte', deleted_at__lte))
            
        if identifier is not None:
            
            _query_params.append(('identifier', identifier))
            
        if is_deleted is not None:
            
            _query_params.append(('is_deleted', is_deleted))
            
        if is_highest_primary_identifier is not None:
            
            _query_params.append(('is_highest_primary_identifier', is_highest_primary_identifier))
            
        if page_size is not None:
            
            _query_params.append(('page_size', page_size))
            
        if retain_until__gte is not None:
            if isinstance(retain_until__gte, datetime):
                _query_params.append(
                    (
                        'retain_until__gte',
                        retain_until__gte.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('retain_until__gte', retain_until__gte))
            
        if retain_until__isnull is not None:
            
            _query_params.append(('retain_until__isnull', retain_until__isnull))
            
        if retain_until__lte is not None:
            if isinstance(retain_until__lte, datetime):
                _query_params.append(
                    (
                        'retain_until__lte',
                        retain_until__lte.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('retain_until__lte', retain_until__lte))
            
        if scheme is not None:
            
            _query_params.append(('scheme', scheme))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/card-identifiers',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_identifiers_retrieve(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card identifier.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CardIdentifier:
        """Get card identifier detail

         ## Get card identifier detail  Allows the detail of a single Card Identifier to be retrieved by identifier UUID. The Card Identifier entity returned contains the information as presented in the list operation above plus additional fields.  > **WARNING!** > > A barcode identifier (`barcode.v1.card.university.identifiers.cam.ac.uk`) may be associated with more than one user. See `Known Issues` for more details.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view the card identifier detail of any card identifier contained within the card system.  

        :param id: A UUID string identifying this card identifier. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_identifiers_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardIdentifier",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_identifiers_retrieve_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card identifier.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CardIdentifier]:
        """Get card identifier detail

         ## Get card identifier detail  Allows the detail of a single Card Identifier to be retrieved by identifier UUID. The Card Identifier entity returned contains the information as presented in the list operation above plus additional fields.  > **WARNING!** > > A barcode identifier (`barcode.v1.card.university.identifiers.cam.ac.uk`) may be associated with more than one user. See `Known Issues` for more details.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view the card identifier detail of any card identifier contained within the card system.  

        :param id: A UUID string identifying this card identifier. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_identifiers_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardIdentifier",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_identifiers_retrieve_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card identifier.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get card identifier detail

         ## Get card identifier detail  Allows the detail of a single Card Identifier to be retrieved by identifier UUID. The Card Identifier entity returned contains the information as presented in the list operation above plus additional fields.  > **WARNING!** > > A barcode identifier (`barcode.v1.card.university.identifiers.cam.ac.uk`) may be associated with more than one user. See `Known Issues` for more details.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view the card identifier detail of any card identifier contained within the card system.  

        :param id: A UUID string identifying this card identifier. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_identifiers_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardIdentifier",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_identifiers_retrieve_serialize(
        self,
        id,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/card-identifiers/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_identifiers_update(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card identifier.")],
        card_identifier_update_request: CardIdentifierUpdateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CardIdentifierUpdateResponseType:
        """Updates the card identifier

         ## Update the card identifier  This method allows a client to submit an action in the request body for a given card identifier. The allowed actions are `repair`, `restore`, `soft_delete` and `hard_delete`.  ### Permissions  Principals with the `CARD_ADMIN` permission will be able to affect this endpoint.   

        :param id: A UUID string identifying this card identifier. (required)
        :type id: str
        :param card_identifier_update_request: (required)
        :type card_identifier_update_request: CardIdentifierUpdateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_identifiers_update_serialize(
            id=id,
            card_identifier_update_request=card_identifier_update_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardIdentifierUpdateResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_identifiers_update_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card identifier.")],
        card_identifier_update_request: CardIdentifierUpdateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CardIdentifierUpdateResponseType]:
        """Updates the card identifier

         ## Update the card identifier  This method allows a client to submit an action in the request body for a given card identifier. The allowed actions are `repair`, `restore`, `soft_delete` and `hard_delete`.  ### Permissions  Principals with the `CARD_ADMIN` permission will be able to affect this endpoint.   

        :param id: A UUID string identifying this card identifier. (required)
        :type id: str
        :param card_identifier_update_request: (required)
        :type card_identifier_update_request: CardIdentifierUpdateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_identifiers_update_serialize(
            id=id,
            card_identifier_update_request=card_identifier_update_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardIdentifierUpdateResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_identifiers_update_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card identifier.")],
        card_identifier_update_request: CardIdentifierUpdateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Updates the card identifier

         ## Update the card identifier  This method allows a client to submit an action in the request body for a given card identifier. The allowed actions are `repair`, `restore`, `soft_delete` and `hard_delete`.  ### Permissions  Principals with the `CARD_ADMIN` permission will be able to affect this endpoint.   

        :param id: A UUID string identifying this card identifier. (required)
        :type id: str
        :param card_identifier_update_request: (required)
        :type card_identifier_update_request: CardIdentifierUpdateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_identifiers_update_serialize(
            id=id,
            card_identifier_update_request=card_identifier_update_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardIdentifierUpdateResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_identifiers_update_serialize(
        self,
        id,
        card_identifier_update_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if card_identifier_update_request is not None:
            _body_params = card_identifier_update_request


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json', 
                        'application/x-www-form-urlencoded', 
                        'multipart/form-data'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='PUT',
            resource_path='/v1beta1/card-identifiers/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_identifiers_update_update(
        self,
        card_identifier_bulk_update_request: CardIdentifierBulkUpdateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CardIdentifierBulkUpdateResponseType:
        """Update multiple card identifiers

         ## Update multiple card identifiers  Allows multiple card identifiers to be updated in one call. For large number of card identifiers, this endpoint will be faster than PUT-ing each update.  Updates are processed in the order they are received. The response includes the detail of the operation, the UUID of the card identifier that was updated, and HTTP status code which would have been returned from separate PUTs. If the status code is 404, the `id` property is omitted.  ### Permissions  Principals with the `CARD_ADMIN` permission will be able to affect this endpoint.  

        :param card_identifier_bulk_update_request: (required)
        :type card_identifier_bulk_update_request: CardIdentifierBulkUpdateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_identifiers_update_update_serialize(
            card_identifier_bulk_update_request=card_identifier_bulk_update_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardIdentifierBulkUpdateResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_identifiers_update_update_with_http_info(
        self,
        card_identifier_bulk_update_request: CardIdentifierBulkUpdateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CardIdentifierBulkUpdateResponseType]:
        """Update multiple card identifiers

         ## Update multiple card identifiers  Allows multiple card identifiers to be updated in one call. For large number of card identifiers, this endpoint will be faster than PUT-ing each update.  Updates are processed in the order they are received. The response includes the detail of the operation, the UUID of the card identifier that was updated, and HTTP status code which would have been returned from separate PUTs. If the status code is 404, the `id` property is omitted.  ### Permissions  Principals with the `CARD_ADMIN` permission will be able to affect this endpoint.  

        :param card_identifier_bulk_update_request: (required)
        :type card_identifier_bulk_update_request: CardIdentifierBulkUpdateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_identifiers_update_update_serialize(
            card_identifier_bulk_update_request=card_identifier_bulk_update_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardIdentifierBulkUpdateResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_identifiers_update_update_without_preload_content(
        self,
        card_identifier_bulk_update_request: CardIdentifierBulkUpdateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update multiple card identifiers

         ## Update multiple card identifiers  Allows multiple card identifiers to be updated in one call. For large number of card identifiers, this endpoint will be faster than PUT-ing each update.  Updates are processed in the order they are received. The response includes the detail of the operation, the UUID of the card identifier that was updated, and HTTP status code which would have been returned from separate PUTs. If the status code is 404, the `id` property is omitted.  ### Permissions  Principals with the `CARD_ADMIN` permission will be able to affect this endpoint.  

        :param card_identifier_bulk_update_request: (required)
        :type card_identifier_bulk_update_request: CardIdentifierBulkUpdateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_identifiers_update_update_serialize(
            card_identifier_bulk_update_request=card_identifier_bulk_update_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardIdentifierBulkUpdateResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_identifiers_update_update_serialize(
        self,
        card_identifier_bulk_update_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if card_identifier_bulk_update_request is not None:
            _body_params = card_identifier_bulk_update_request


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json', 
                        'application/x-www-form-urlencoded', 
                        'multipart/form-data'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='PUT',
            resource_path='/v1beta1/card-identifiers/update',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_logos_content_retrieve(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card logo.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> None:
        """Get card logo image content

         ## Get Card Logo Image Content  Redirects to the image content for a given card logo. Note that this endpoint will redirect to a temporary URL provided by the storage provider. This URL will timeout after a short period of time and therefore should not be persisted.  

        :param id: A UUID string identifying this card logo. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_logos_content_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '302': None,
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_logos_content_retrieve_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card logo.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[None]:
        """Get card logo image content

         ## Get Card Logo Image Content  Redirects to the image content for a given card logo. Note that this endpoint will redirect to a temporary URL provided by the storage provider. This URL will timeout after a short period of time and therefore should not be persisted.  

        :param id: A UUID string identifying this card logo. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_logos_content_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '302': None,
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_logos_content_retrieve_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card logo.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get card logo image content

         ## Get Card Logo Image Content  Redirects to the image content for a given card logo. Note that this endpoint will redirect to a temporary URL provided by the storage provider. This URL will timeout after a short period of time and therefore should not be persisted.  

        :param id: A UUID string identifying this card logo. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_logos_content_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '302': None,
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_logos_content_retrieve_serialize(
        self,
        id,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/card-logos/{id}/content',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_logos_list(
        self,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> PaginatedCardLogoList:
        """List card logos

         ## List Card Logos  Returns a list of card logo objects - representing logos which can be displayed on cards.  Each logo contains a `contentLink` which links to the image content for this logo. The rest of the object represents metadata about a logo.  

        :param cursor: The pagination cursor value.
        :type cursor: str
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_logos_list_serialize(
            cursor=cursor,
            page_size=page_size,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCardLogoList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_logos_list_with_http_info(
        self,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[PaginatedCardLogoList]:
        """List card logos

         ## List Card Logos  Returns a list of card logo objects - representing logos which can be displayed on cards.  Each logo contains a `contentLink` which links to the image content for this logo. The rest of the object represents metadata about a logo.  

        :param cursor: The pagination cursor value.
        :type cursor: str
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_logos_list_serialize(
            cursor=cursor,
            page_size=page_size,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCardLogoList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_logos_list_without_preload_content(
        self,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """List card logos

         ## List Card Logos  Returns a list of card logo objects - representing logos which can be displayed on cards.  Each logo contains a `contentLink` which links to the image content for this logo. The rest of the object represents metadata about a logo.  

        :param cursor: The pagination cursor value.
        :type cursor: str
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_logos_list_serialize(
            cursor=cursor,
            page_size=page_size,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCardLogoList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_logos_list_serialize(
        self,
        cursor,
        page_size,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if cursor is not None:
            
            _query_params.append(('cursor', cursor))
            
        if page_size is not None:
            
            _query_params.append(('page_size', page_size))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/card-logos',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_logos_retrieve(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card logo.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CardLogo:
        """Get card logo detail

         ## Get Card Logo  Returns a single card logo by UUID - containing metadata about a logo that can be present on a card.  

        :param id: A UUID string identifying this card logo. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_logos_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardLogo",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_logos_retrieve_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card logo.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CardLogo]:
        """Get card logo detail

         ## Get Card Logo  Returns a single card logo by UUID - containing metadata about a logo that can be present on a card.  

        :param id: A UUID string identifying this card logo. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_logos_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardLogo",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_logos_retrieve_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card logo.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get card logo detail

         ## Get Card Logo  Returns a single card logo by UUID - containing metadata about a logo that can be present on a card.  

        :param id: A UUID string identifying this card logo. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_logos_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardLogo",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_logos_retrieve_serialize(
        self,
        id,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/card-logos/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_notes_create(
        self,
        card_note_create_request_type_request: CardNoteCreateRequestTypeRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CardNote:
        """Creates a card note

         ## Create card note  This method allows the client to create a card note for a given card.  ### Permissions  Principals with the `CARD_NOTE_CREATOR` permission will be able to affect this endpoint.  

        :param card_note_create_request_type_request: (required)
        :type card_note_create_request_type_request: CardNoteCreateRequestTypeRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_notes_create_serialize(
            card_note_create_request_type_request=card_note_create_request_type_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '201': "CardNote",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_notes_create_with_http_info(
        self,
        card_note_create_request_type_request: CardNoteCreateRequestTypeRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CardNote]:
        """Creates a card note

         ## Create card note  This method allows the client to create a card note for a given card.  ### Permissions  Principals with the `CARD_NOTE_CREATOR` permission will be able to affect this endpoint.  

        :param card_note_create_request_type_request: (required)
        :type card_note_create_request_type_request: CardNoteCreateRequestTypeRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_notes_create_serialize(
            card_note_create_request_type_request=card_note_create_request_type_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '201': "CardNote",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_notes_create_without_preload_content(
        self,
        card_note_create_request_type_request: CardNoteCreateRequestTypeRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Creates a card note

         ## Create card note  This method allows the client to create a card note for a given card.  ### Permissions  Principals with the `CARD_NOTE_CREATOR` permission will be able to affect this endpoint.  

        :param card_note_create_request_type_request: (required)
        :type card_note_create_request_type_request: CardNoteCreateRequestTypeRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_notes_create_serialize(
            card_note_create_request_type_request=card_note_create_request_type_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '201': "CardNote",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_notes_create_serialize(
        self,
        card_note_create_request_type_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if card_note_create_request_type_request is not None:
            _body_params = card_note_create_request_type_request


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json', 
                        'application/x-www-form-urlencoded', 
                        'multipart/form-data'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/v1beta1/card-notes',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_notes_destroy(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card note.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CardNoteDestroyResponseType:
        """Deletes a card note

         ## Delete card note  This method allows the client to delete a given card note.  ### Permissions  Principals with the `CARD_NOTE_CREATOR` permission who created the card note instance will be able to affect this endpoint.  Principals with the `CARD_NOTE_UPDATER` permission will be able to affect this endpoint.  

        :param id: A UUID string identifying this card note. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_notes_destroy_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardNoteDestroyResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_notes_destroy_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card note.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CardNoteDestroyResponseType]:
        """Deletes a card note

         ## Delete card note  This method allows the client to delete a given card note.  ### Permissions  Principals with the `CARD_NOTE_CREATOR` permission who created the card note instance will be able to affect this endpoint.  Principals with the `CARD_NOTE_UPDATER` permission will be able to affect this endpoint.  

        :param id: A UUID string identifying this card note. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_notes_destroy_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardNoteDestroyResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_notes_destroy_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card note.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Deletes a card note

         ## Delete card note  This method allows the client to delete a given card note.  ### Permissions  Principals with the `CARD_NOTE_CREATOR` permission who created the card note instance will be able to affect this endpoint.  Principals with the `CARD_NOTE_UPDATER` permission will be able to affect this endpoint.  

        :param id: A UUID string identifying this card note. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_notes_destroy_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardNoteDestroyResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_notes_destroy_serialize(
        self,
        id,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='DELETE',
            resource_path='/v1beta1/card-notes/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_notes_list(
        self,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> PaginatedCardNoteList:
        """v1beta1_card_notes_list


        :param cursor: The pagination cursor value.
        :type cursor: str
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_notes_list_serialize(
            cursor=cursor,
            page_size=page_size,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCardNoteList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_notes_list_with_http_info(
        self,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[PaginatedCardNoteList]:
        """v1beta1_card_notes_list


        :param cursor: The pagination cursor value.
        :type cursor: str
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_notes_list_serialize(
            cursor=cursor,
            page_size=page_size,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCardNoteList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_notes_list_without_preload_content(
        self,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """v1beta1_card_notes_list


        :param cursor: The pagination cursor value.
        :type cursor: str
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_notes_list_serialize(
            cursor=cursor,
            page_size=page_size,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCardNoteList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_notes_list_serialize(
        self,
        cursor,
        page_size,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if cursor is not None:
            
            _query_params.append(('cursor', cursor))
            
        if page_size is not None:
            
            _query_params.append(('page_size', page_size))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/card-notes',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_notes_retrieve(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card note.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CardNote:
        """v1beta1_card_notes_retrieve


        :param id: A UUID string identifying this card note. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_notes_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardNote",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_notes_retrieve_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card note.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CardNote]:
        """v1beta1_card_notes_retrieve


        :param id: A UUID string identifying this card note. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_notes_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardNote",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_notes_retrieve_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card note.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """v1beta1_card_notes_retrieve


        :param id: A UUID string identifying this card note. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_notes_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardNote",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_notes_retrieve_serialize(
        self,
        id,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/card-notes/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_requests_back_visualization_retrieve(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card request.")],
        format: Optional[StrictStr] = None,
        height: Annotated[Optional[StrictInt], Field(description="The desired height of the visualization (in pixels)")] = None,
        width: Annotated[Optional[StrictInt], Field(description="The desired width of the visualization (in pixels)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> bytearray:
        """Returns a representation of the back of this card request

         ## Get card back visualization  Returns a visualization of the back of this card in BMP, PNG or SVG format.  Currently a placeholder is used to represent the barcode printed on the back of the card, this will be replaced with a valid barcode as a piece of follow-up work.  Temporary cards cannot be visualized, and will simply return a blank image.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view visualization of any card contained within the card system. Principals without this permission are only able to view the visualization for a card that they own. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param id: A UUID string identifying this card request. (required)
        :type id: str
        :param format:
        :type format: str
        :param height: The desired height of the visualization (in pixels)
        :type height: int
        :param width: The desired width of the visualization (in pixels)
        :type width: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_back_visualization_retrieve_serialize(
            id=id,
            format=format,
            height=height,
            width=width,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "bytearray",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_requests_back_visualization_retrieve_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card request.")],
        format: Optional[StrictStr] = None,
        height: Annotated[Optional[StrictInt], Field(description="The desired height of the visualization (in pixels)")] = None,
        width: Annotated[Optional[StrictInt], Field(description="The desired width of the visualization (in pixels)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[bytearray]:
        """Returns a representation of the back of this card request

         ## Get card back visualization  Returns a visualization of the back of this card in BMP, PNG or SVG format.  Currently a placeholder is used to represent the barcode printed on the back of the card, this will be replaced with a valid barcode as a piece of follow-up work.  Temporary cards cannot be visualized, and will simply return a blank image.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view visualization of any card contained within the card system. Principals without this permission are only able to view the visualization for a card that they own. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param id: A UUID string identifying this card request. (required)
        :type id: str
        :param format:
        :type format: str
        :param height: The desired height of the visualization (in pixels)
        :type height: int
        :param width: The desired width of the visualization (in pixels)
        :type width: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_back_visualization_retrieve_serialize(
            id=id,
            format=format,
            height=height,
            width=width,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "bytearray",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_requests_back_visualization_retrieve_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card request.")],
        format: Optional[StrictStr] = None,
        height: Annotated[Optional[StrictInt], Field(description="The desired height of the visualization (in pixels)")] = None,
        width: Annotated[Optional[StrictInt], Field(description="The desired width of the visualization (in pixels)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Returns a representation of the back of this card request

         ## Get card back visualization  Returns a visualization of the back of this card in BMP, PNG or SVG format.  Currently a placeholder is used to represent the barcode printed on the back of the card, this will be replaced with a valid barcode as a piece of follow-up work.  Temporary cards cannot be visualized, and will simply return a blank image.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view visualization of any card contained within the card system. Principals without this permission are only able to view the visualization for a card that they own. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param id: A UUID string identifying this card request. (required)
        :type id: str
        :param format:
        :type format: str
        :param height: The desired height of the visualization (in pixels)
        :type height: int
        :param width: The desired width of the visualization (in pixels)
        :type width: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_back_visualization_retrieve_serialize(
            id=id,
            format=format,
            height=height,
            width=width,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "bytearray",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_requests_back_visualization_retrieve_serialize(
        self,
        id,
        format,
        height,
        width,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        if format is not None:
            
            _query_params.append(('format', format))
            
        if height is not None:
            
            _query_params.append(('height', height))
            
        if width is not None:
            
            _query_params.append(('width', width))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'image/bmp', 
                'image/png', 
                'image/svg+xml'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/card-requests/{id}/back-visualization',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_requests_cardholder_statuses_retrieve(
        self,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CardRequestDistinctValues:
        """Returns all cardholder statuses present on card requests

        Returns the distinct cardholder statuses present on card requests.

        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_cardholder_statuses_retrieve_serialize(
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRequestDistinctValues",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_requests_cardholder_statuses_retrieve_with_http_info(
        self,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CardRequestDistinctValues]:
        """Returns all cardholder statuses present on card requests

        Returns the distinct cardholder statuses present on card requests.

        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_cardholder_statuses_retrieve_serialize(
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRequestDistinctValues",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_requests_cardholder_statuses_retrieve_without_preload_content(
        self,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Returns all cardholder statuses present on card requests

        Returns the distinct cardholder statuses present on card requests.

        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_cardholder_statuses_retrieve_serialize(
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRequestDistinctValues",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_requests_cardholder_statuses_retrieve_serialize(
        self,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/card-requests/cardholder-statuses',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_requests_create(
        self,
        card_request_create_type_request: CardRequestCreateTypeRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CardRequest:
        """Creates a card request

         ## Create a card request  This method allows the client to create a card request for a given identifier. The identifier should be provided in the format `<value>@<scheme>`.  Only the `v1.person.identifiers.cam.ac.uk` scheme is supported at present.  ### Permission  Principals with the `CARD_REQUEST_CREATOR` permission will be able to affect this endpoint.  

        :param card_request_create_type_request: (required)
        :type card_request_create_type_request: CardRequestCreateTypeRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_create_serialize(
            card_request_create_type_request=card_request_create_type_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '201': "CardRequest",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_requests_create_with_http_info(
        self,
        card_request_create_type_request: CardRequestCreateTypeRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CardRequest]:
        """Creates a card request

         ## Create a card request  This method allows the client to create a card request for a given identifier. The identifier should be provided in the format `<value>@<scheme>`.  Only the `v1.person.identifiers.cam.ac.uk` scheme is supported at present.  ### Permission  Principals with the `CARD_REQUEST_CREATOR` permission will be able to affect this endpoint.  

        :param card_request_create_type_request: (required)
        :type card_request_create_type_request: CardRequestCreateTypeRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_create_serialize(
            card_request_create_type_request=card_request_create_type_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '201': "CardRequest",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_requests_create_without_preload_content(
        self,
        card_request_create_type_request: CardRequestCreateTypeRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Creates a card request

         ## Create a card request  This method allows the client to create a card request for a given identifier. The identifier should be provided in the format `<value>@<scheme>`.  Only the `v1.person.identifiers.cam.ac.uk` scheme is supported at present.  ### Permission  Principals with the `CARD_REQUEST_CREATOR` permission will be able to affect this endpoint.  

        :param card_request_create_type_request: (required)
        :type card_request_create_type_request: CardRequestCreateTypeRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_create_serialize(
            card_request_create_type_request=card_request_create_type_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '201': "CardRequest",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_requests_create_serialize(
        self,
        card_request_create_type_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if card_request_create_type_request is not None:
            _body_params = card_request_create_type_request


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json', 
                        'application/x-www-form-urlencoded', 
                        'multipart/form-data'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/v1beta1/card-requests',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_requests_destinations_retrieve(
        self,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CardRequestDistinctValues:
        """Returns the destinations of all card requests

        Returns the distinct destinations of all card requests.

        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_destinations_retrieve_serialize(
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRequestDistinctValues",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_requests_destinations_retrieve_with_http_info(
        self,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CardRequestDistinctValues]:
        """Returns the destinations of all card requests

        Returns the distinct destinations of all card requests.

        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_destinations_retrieve_serialize(
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRequestDistinctValues",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_requests_destinations_retrieve_without_preload_content(
        self,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Returns the destinations of all card requests

        Returns the distinct destinations of all card requests.

        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_destinations_retrieve_serialize(
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRequestDistinctValues",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_requests_destinations_retrieve_serialize(
        self,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/card-requests/destinations',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_requests_front_visualization_retrieve(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card request.")],
        format: Optional[StrictStr] = None,
        height: Annotated[Optional[StrictInt], Field(description="The desired height of the visualization (in pixels)")] = None,
        render_placeholder: Annotated[Optional[StrictBool], Field(description="Whether to render a placeholder image when the photo associated with the card cannot be found")] = None,
        width: Annotated[Optional[StrictInt], Field(description="The desired width of the visualization (in pixels)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> bytearray:
        """Returns a representation of the front of this card request

         ## Get card front visualization  Returns a visualization of the front of this card in BMP, PNG or SVG format. Makes use of the Photo API to fetch the photo of the cardholder used on this card. In cases where this card makes use of an out-of-date photo of the cardholder imported from the legacy card system, the Photo may not be available, in which case a placeholder is displayed unless the `render_placeholder` query parameter is set to `false`.  Temporary cards cannot be visualized, and will simply return a blank image.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view visualization of any card contained within the card system. Principals without this permission are only able to view the visualization for a card that they own. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param id: A UUID string identifying this card request. (required)
        :type id: str
        :param format:
        :type format: str
        :param height: The desired height of the visualization (in pixels)
        :type height: int
        :param render_placeholder: Whether to render a placeholder image when the photo associated with the card cannot be found
        :type render_placeholder: bool
        :param width: The desired width of the visualization (in pixels)
        :type width: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_front_visualization_retrieve_serialize(
            id=id,
            format=format,
            height=height,
            render_placeholder=render_placeholder,
            width=width,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "bytearray",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_requests_front_visualization_retrieve_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card request.")],
        format: Optional[StrictStr] = None,
        height: Annotated[Optional[StrictInt], Field(description="The desired height of the visualization (in pixels)")] = None,
        render_placeholder: Annotated[Optional[StrictBool], Field(description="Whether to render a placeholder image when the photo associated with the card cannot be found")] = None,
        width: Annotated[Optional[StrictInt], Field(description="The desired width of the visualization (in pixels)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[bytearray]:
        """Returns a representation of the front of this card request

         ## Get card front visualization  Returns a visualization of the front of this card in BMP, PNG or SVG format. Makes use of the Photo API to fetch the photo of the cardholder used on this card. In cases where this card makes use of an out-of-date photo of the cardholder imported from the legacy card system, the Photo may not be available, in which case a placeholder is displayed unless the `render_placeholder` query parameter is set to `false`.  Temporary cards cannot be visualized, and will simply return a blank image.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view visualization of any card contained within the card system. Principals without this permission are only able to view the visualization for a card that they own. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param id: A UUID string identifying this card request. (required)
        :type id: str
        :param format:
        :type format: str
        :param height: The desired height of the visualization (in pixels)
        :type height: int
        :param render_placeholder: Whether to render a placeholder image when the photo associated with the card cannot be found
        :type render_placeholder: bool
        :param width: The desired width of the visualization (in pixels)
        :type width: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_front_visualization_retrieve_serialize(
            id=id,
            format=format,
            height=height,
            render_placeholder=render_placeholder,
            width=width,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "bytearray",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_requests_front_visualization_retrieve_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card request.")],
        format: Optional[StrictStr] = None,
        height: Annotated[Optional[StrictInt], Field(description="The desired height of the visualization (in pixels)")] = None,
        render_placeholder: Annotated[Optional[StrictBool], Field(description="Whether to render a placeholder image when the photo associated with the card cannot be found")] = None,
        width: Annotated[Optional[StrictInt], Field(description="The desired width of the visualization (in pixels)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Returns a representation of the front of this card request

         ## Get card front visualization  Returns a visualization of the front of this card in BMP, PNG or SVG format. Makes use of the Photo API to fetch the photo of the cardholder used on this card. In cases where this card makes use of an out-of-date photo of the cardholder imported from the legacy card system, the Photo may not be available, in which case a placeholder is displayed unless the `render_placeholder` query parameter is set to `false`.  Temporary cards cannot be visualized, and will simply return a blank image.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view visualization of any card contained within the card system. Principals without this permission are only able to view the visualization for a card that they own. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param id: A UUID string identifying this card request. (required)
        :type id: str
        :param format:
        :type format: str
        :param height: The desired height of the visualization (in pixels)
        :type height: int
        :param render_placeholder: Whether to render a placeholder image when the photo associated with the card cannot be found
        :type render_placeholder: bool
        :param width: The desired width of the visualization (in pixels)
        :type width: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_front_visualization_retrieve_serialize(
            id=id,
            format=format,
            height=height,
            render_placeholder=render_placeholder,
            width=width,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "bytearray",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_requests_front_visualization_retrieve_serialize(
        self,
        id,
        format,
        height,
        render_placeholder,
        width,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        if format is not None:
            
            _query_params.append(('format', format))
            
        if height is not None:
            
            _query_params.append(('height', height))
            
        if render_placeholder is not None:
            
            _query_params.append(('render_placeholder', render_placeholder))
            
        if width is not None:
            
            _query_params.append(('width', width))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'image/bmp', 
                'image/png', 
                'image/svg+xml'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/card-requests/{id}/front-visualization',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_requests_list(
        self,
        card_type: Annotated[Optional[StrictStr], Field(description="Type  * `MIFARE_PERSONAL` - Personal * `MIFARE_TEMPORARY` - Temporary")] = None,
        cardholder_status: Optional[StrictStr] = None,
        created_at__gte: Optional[datetime] = None,
        created_at__lte: Optional[datetime] = None,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        destination: Optional[StrictStr] = None,
        identifier: Annotated[Optional[StrictStr], Field(description="Email-formatted identifier")] = None,
        ordering: Annotated[Optional[StrictStr], Field(description="Which field to use when ordering the results.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        requestor: Optional[StrictStr] = None,
        updated_at__gte: Optional[datetime] = None,
        updated_at__lte: Optional[datetime] = None,
        workflow_state: Annotated[Optional[List[StrictStr]], Field(description="Workflow state  * `PENDING` - Pending * `HOLD` - Hold * `CANCELLED` - Cancelled * `CREATING_TODO` - ToDo * `CREATING_INPROGRESS` - InProgress * `CREATING_INVERIFICATION` - InVerification * `CREATING_DONE` - Done * `PENDING_CRSID_REQUIRED` - PendingCRSidRequired * `PENDING_PHOTO_REQUIRED` - PendingPhotoRequired * `PENDING_DESTINATION_REQUIRED` - PendingDestinationRequired * `PENDING_EXPIRY_DATA_REQUIRED` - PendingExpiryDataRequired")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> PaginatedCardRequestSummaryList:
        """List card requests

         ## List Card Requests  Returns a list of card request objects - representing requests for card creation.  > **WARNING!** > > A barcode identifier (`barcode.v1.card.university.identifiers.cam.ac.uk`) may be associated with more than one user. See `Known Issues` for more details.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view all card requests contained within the card system. Without this permission only card requests owned by the authenticated principal will be returned. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param card_type: Type  * `MIFARE_PERSONAL` - Personal * `MIFARE_TEMPORARY` - Temporary
        :type card_type: str
        :param cardholder_status:
        :type cardholder_status: str
        :param created_at__gte:
        :type created_at__gte: datetime
        :param created_at__lte:
        :type created_at__lte: datetime
        :param cursor: The pagination cursor value.
        :type cursor: str
        :param destination:
        :type destination: str
        :param identifier: Email-formatted identifier
        :type identifier: str
        :param ordering: Which field to use when ordering the results.
        :type ordering: str
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param requestor:
        :type requestor: str
        :param updated_at__gte:
        :type updated_at__gte: datetime
        :param updated_at__lte:
        :type updated_at__lte: datetime
        :param workflow_state: Workflow state  * `PENDING` - Pending * `HOLD` - Hold * `CANCELLED` - Cancelled * `CREATING_TODO` - ToDo * `CREATING_INPROGRESS` - InProgress * `CREATING_INVERIFICATION` - InVerification * `CREATING_DONE` - Done * `PENDING_CRSID_REQUIRED` - PendingCRSidRequired * `PENDING_PHOTO_REQUIRED` - PendingPhotoRequired * `PENDING_DESTINATION_REQUIRED` - PendingDestinationRequired * `PENDING_EXPIRY_DATA_REQUIRED` - PendingExpiryDataRequired
        :type workflow_state: List[str]
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_list_serialize(
            card_type=card_type,
            cardholder_status=cardholder_status,
            created_at__gte=created_at__gte,
            created_at__lte=created_at__lte,
            cursor=cursor,
            destination=destination,
            identifier=identifier,
            ordering=ordering,
            page_size=page_size,
            requestor=requestor,
            updated_at__gte=updated_at__gte,
            updated_at__lte=updated_at__lte,
            workflow_state=workflow_state,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCardRequestSummaryList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_requests_list_with_http_info(
        self,
        card_type: Annotated[Optional[StrictStr], Field(description="Type  * `MIFARE_PERSONAL` - Personal * `MIFARE_TEMPORARY` - Temporary")] = None,
        cardholder_status: Optional[StrictStr] = None,
        created_at__gte: Optional[datetime] = None,
        created_at__lte: Optional[datetime] = None,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        destination: Optional[StrictStr] = None,
        identifier: Annotated[Optional[StrictStr], Field(description="Email-formatted identifier")] = None,
        ordering: Annotated[Optional[StrictStr], Field(description="Which field to use when ordering the results.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        requestor: Optional[StrictStr] = None,
        updated_at__gte: Optional[datetime] = None,
        updated_at__lte: Optional[datetime] = None,
        workflow_state: Annotated[Optional[List[StrictStr]], Field(description="Workflow state  * `PENDING` - Pending * `HOLD` - Hold * `CANCELLED` - Cancelled * `CREATING_TODO` - ToDo * `CREATING_INPROGRESS` - InProgress * `CREATING_INVERIFICATION` - InVerification * `CREATING_DONE` - Done * `PENDING_CRSID_REQUIRED` - PendingCRSidRequired * `PENDING_PHOTO_REQUIRED` - PendingPhotoRequired * `PENDING_DESTINATION_REQUIRED` - PendingDestinationRequired * `PENDING_EXPIRY_DATA_REQUIRED` - PendingExpiryDataRequired")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[PaginatedCardRequestSummaryList]:
        """List card requests

         ## List Card Requests  Returns a list of card request objects - representing requests for card creation.  > **WARNING!** > > A barcode identifier (`barcode.v1.card.university.identifiers.cam.ac.uk`) may be associated with more than one user. See `Known Issues` for more details.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view all card requests contained within the card system. Without this permission only card requests owned by the authenticated principal will be returned. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param card_type: Type  * `MIFARE_PERSONAL` - Personal * `MIFARE_TEMPORARY` - Temporary
        :type card_type: str
        :param cardholder_status:
        :type cardholder_status: str
        :param created_at__gte:
        :type created_at__gte: datetime
        :param created_at__lte:
        :type created_at__lte: datetime
        :param cursor: The pagination cursor value.
        :type cursor: str
        :param destination:
        :type destination: str
        :param identifier: Email-formatted identifier
        :type identifier: str
        :param ordering: Which field to use when ordering the results.
        :type ordering: str
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param requestor:
        :type requestor: str
        :param updated_at__gte:
        :type updated_at__gte: datetime
        :param updated_at__lte:
        :type updated_at__lte: datetime
        :param workflow_state: Workflow state  * `PENDING` - Pending * `HOLD` - Hold * `CANCELLED` - Cancelled * `CREATING_TODO` - ToDo * `CREATING_INPROGRESS` - InProgress * `CREATING_INVERIFICATION` - InVerification * `CREATING_DONE` - Done * `PENDING_CRSID_REQUIRED` - PendingCRSidRequired * `PENDING_PHOTO_REQUIRED` - PendingPhotoRequired * `PENDING_DESTINATION_REQUIRED` - PendingDestinationRequired * `PENDING_EXPIRY_DATA_REQUIRED` - PendingExpiryDataRequired
        :type workflow_state: List[str]
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_list_serialize(
            card_type=card_type,
            cardholder_status=cardholder_status,
            created_at__gte=created_at__gte,
            created_at__lte=created_at__lte,
            cursor=cursor,
            destination=destination,
            identifier=identifier,
            ordering=ordering,
            page_size=page_size,
            requestor=requestor,
            updated_at__gte=updated_at__gte,
            updated_at__lte=updated_at__lte,
            workflow_state=workflow_state,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCardRequestSummaryList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_requests_list_without_preload_content(
        self,
        card_type: Annotated[Optional[StrictStr], Field(description="Type  * `MIFARE_PERSONAL` - Personal * `MIFARE_TEMPORARY` - Temporary")] = None,
        cardholder_status: Optional[StrictStr] = None,
        created_at__gte: Optional[datetime] = None,
        created_at__lte: Optional[datetime] = None,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        destination: Optional[StrictStr] = None,
        identifier: Annotated[Optional[StrictStr], Field(description="Email-formatted identifier")] = None,
        ordering: Annotated[Optional[StrictStr], Field(description="Which field to use when ordering the results.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        requestor: Optional[StrictStr] = None,
        updated_at__gte: Optional[datetime] = None,
        updated_at__lte: Optional[datetime] = None,
        workflow_state: Annotated[Optional[List[StrictStr]], Field(description="Workflow state  * `PENDING` - Pending * `HOLD` - Hold * `CANCELLED` - Cancelled * `CREATING_TODO` - ToDo * `CREATING_INPROGRESS` - InProgress * `CREATING_INVERIFICATION` - InVerification * `CREATING_DONE` - Done * `PENDING_CRSID_REQUIRED` - PendingCRSidRequired * `PENDING_PHOTO_REQUIRED` - PendingPhotoRequired * `PENDING_DESTINATION_REQUIRED` - PendingDestinationRequired * `PENDING_EXPIRY_DATA_REQUIRED` - PendingExpiryDataRequired")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """List card requests

         ## List Card Requests  Returns a list of card request objects - representing requests for card creation.  > **WARNING!** > > A barcode identifier (`barcode.v1.card.university.identifiers.cam.ac.uk`) may be associated with more than one user. See `Known Issues` for more details.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view all card requests contained within the card system. Without this permission only card requests owned by the authenticated principal will be returned. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param card_type: Type  * `MIFARE_PERSONAL` - Personal * `MIFARE_TEMPORARY` - Temporary
        :type card_type: str
        :param cardholder_status:
        :type cardholder_status: str
        :param created_at__gte:
        :type created_at__gte: datetime
        :param created_at__lte:
        :type created_at__lte: datetime
        :param cursor: The pagination cursor value.
        :type cursor: str
        :param destination:
        :type destination: str
        :param identifier: Email-formatted identifier
        :type identifier: str
        :param ordering: Which field to use when ordering the results.
        :type ordering: str
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param requestor:
        :type requestor: str
        :param updated_at__gte:
        :type updated_at__gte: datetime
        :param updated_at__lte:
        :type updated_at__lte: datetime
        :param workflow_state: Workflow state  * `PENDING` - Pending * `HOLD` - Hold * `CANCELLED` - Cancelled * `CREATING_TODO` - ToDo * `CREATING_INPROGRESS` - InProgress * `CREATING_INVERIFICATION` - InVerification * `CREATING_DONE` - Done * `PENDING_CRSID_REQUIRED` - PendingCRSidRequired * `PENDING_PHOTO_REQUIRED` - PendingPhotoRequired * `PENDING_DESTINATION_REQUIRED` - PendingDestinationRequired * `PENDING_EXPIRY_DATA_REQUIRED` - PendingExpiryDataRequired
        :type workflow_state: List[str]
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_list_serialize(
            card_type=card_type,
            cardholder_status=cardholder_status,
            created_at__gte=created_at__gte,
            created_at__lte=created_at__lte,
            cursor=cursor,
            destination=destination,
            identifier=identifier,
            ordering=ordering,
            page_size=page_size,
            requestor=requestor,
            updated_at__gte=updated_at__gte,
            updated_at__lte=updated_at__lte,
            workflow_state=workflow_state,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCardRequestSummaryList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_requests_list_serialize(
        self,
        card_type,
        cardholder_status,
        created_at__gte,
        created_at__lte,
        cursor,
        destination,
        identifier,
        ordering,
        page_size,
        requestor,
        updated_at__gte,
        updated_at__lte,
        workflow_state,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
            'workflow_state': 'multi',
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if card_type is not None:
            
            _query_params.append(('card_type', card_type))
            
        if cardholder_status is not None:
            
            _query_params.append(('cardholder_status', cardholder_status))
            
        if created_at__gte is not None:
            if isinstance(created_at__gte, datetime):
                _query_params.append(
                    (
                        'created_at__gte',
                        created_at__gte.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('created_at__gte', created_at__gte))
            
        if created_at__lte is not None:
            if isinstance(created_at__lte, datetime):
                _query_params.append(
                    (
                        'created_at__lte',
                        created_at__lte.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('created_at__lte', created_at__lte))
            
        if cursor is not None:
            
            _query_params.append(('cursor', cursor))
            
        if destination is not None:
            
            _query_params.append(('destination', destination))
            
        if identifier is not None:
            
            _query_params.append(('identifier', identifier))
            
        if ordering is not None:
            
            _query_params.append(('ordering', ordering))
            
        if page_size is not None:
            
            _query_params.append(('page_size', page_size))
            
        if requestor is not None:
            
            _query_params.append(('requestor', requestor))
            
        if updated_at__gte is not None:
            if isinstance(updated_at__gte, datetime):
                _query_params.append(
                    (
                        'updated_at__gte',
                        updated_at__gte.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('updated_at__gte', updated_at__gte))
            
        if updated_at__lte is not None:
            if isinstance(updated_at__lte, datetime):
                _query_params.append(
                    (
                        'updated_at__lte',
                        updated_at__lte.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('updated_at__lte', updated_at__lte))
            
        if workflow_state is not None:
            
            _query_params.append(('workflow_state', workflow_state))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/card-requests',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_requests_requestors_retrieve(
        self,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CardRequestDistinctValues:
        """Returns the list of people or services who have made a card request

        Returns the distinct people or services who have made a card request.

        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_requestors_retrieve_serialize(
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRequestDistinctValues",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_requests_requestors_retrieve_with_http_info(
        self,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CardRequestDistinctValues]:
        """Returns the list of people or services who have made a card request

        Returns the distinct people or services who have made a card request.

        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_requestors_retrieve_serialize(
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRequestDistinctValues",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_requests_requestors_retrieve_without_preload_content(
        self,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Returns the list of people or services who have made a card request

        Returns the distinct people or services who have made a card request.

        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_requestors_retrieve_serialize(
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRequestDistinctValues",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_requests_requestors_retrieve_serialize(
        self,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/card-requests/requestors',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_requests_retrieve(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card request.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CardRequest:
        """Get card request detail

         ## Get Card Request  Returns a single card request by UUID - containing metadata about a request for card creation.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view all card requests contained within the card system. Without this permission only card requests owned by the authenticated principal are visible. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param id: A UUID string identifying this card request. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRequest",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_requests_retrieve_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card request.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CardRequest]:
        """Get card request detail

         ## Get Card Request  Returns a single card request by UUID - containing metadata about a request for card creation.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view all card requests contained within the card system. Without this permission only card requests owned by the authenticated principal are visible. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param id: A UUID string identifying this card request. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRequest",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_requests_retrieve_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card request.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get card request detail

         ## Get Card Request  Returns a single card request by UUID - containing metadata about a request for card creation.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view all card requests contained within the card system. Without this permission only card requests owned by the authenticated principal are visible. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param id: A UUID string identifying this card request. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRequest",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_requests_retrieve_serialize(
        self,
        id,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/card-requests/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_requests_update(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card request.")],
        card_request_update_request: CardRequestUpdateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CardRequestUpdateResponseType:
        """Updates the card request

         ## Update the card request  This method allows a client to submit an action in the request body and optional identifier for a given card request. The available actions are `update`, `set_hold`, `release_hold`, `add`, `start`, `refresh`, `abandon`, `make`, `requeue`, `complete` and `cancel`.  For the `set_hold` action, the client can optionally append a `hold_reason` field describing the reason for holding the card request.  For the `cancel` action, the client can optionally append a `cancel_reason` field describing the reason for cancelling the card request.  For the `update` action, the client can optionally append `fields` and/or `identifiers` to be updated. An `update` action without `fields` or `identifiers` refreshes the card request by updating the card request data from the data sources.  For the `make` action, the client can also append identifiers which associates the physically created cards to the card record - for example the card UID which is  pre-encoded into the card by the manufacturer.   The `complete` action returns the UUID of the created `card` entity.  ### Permissions  Principals with the `CARD_REQUEST_UPDATER` permission will be able to affect this endpoint.  Principals with the `CARD_REQUEST_CREATOR` permission are able to affect the `update`, `set_hold`, `release_hold` and `cancel` actions for card requests created by the principal.  

        :param id: A UUID string identifying this card request. (required)
        :type id: str
        :param card_request_update_request: (required)
        :type card_request_update_request: CardRequestUpdateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_update_serialize(
            id=id,
            card_request_update_request=card_request_update_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRequestUpdateResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_requests_update_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card request.")],
        card_request_update_request: CardRequestUpdateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CardRequestUpdateResponseType]:
        """Updates the card request

         ## Update the card request  This method allows a client to submit an action in the request body and optional identifier for a given card request. The available actions are `update`, `set_hold`, `release_hold`, `add`, `start`, `refresh`, `abandon`, `make`, `requeue`, `complete` and `cancel`.  For the `set_hold` action, the client can optionally append a `hold_reason` field describing the reason for holding the card request.  For the `cancel` action, the client can optionally append a `cancel_reason` field describing the reason for cancelling the card request.  For the `update` action, the client can optionally append `fields` and/or `identifiers` to be updated. An `update` action without `fields` or `identifiers` refreshes the card request by updating the card request data from the data sources.  For the `make` action, the client can also append identifiers which associates the physically created cards to the card record - for example the card UID which is  pre-encoded into the card by the manufacturer.   The `complete` action returns the UUID of the created `card` entity.  ### Permissions  Principals with the `CARD_REQUEST_UPDATER` permission will be able to affect this endpoint.  Principals with the `CARD_REQUEST_CREATOR` permission are able to affect the `update`, `set_hold`, `release_hold` and `cancel` actions for card requests created by the principal.  

        :param id: A UUID string identifying this card request. (required)
        :type id: str
        :param card_request_update_request: (required)
        :type card_request_update_request: CardRequestUpdateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_update_serialize(
            id=id,
            card_request_update_request=card_request_update_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRequestUpdateResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_requests_update_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card request.")],
        card_request_update_request: CardRequestUpdateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Updates the card request

         ## Update the card request  This method allows a client to submit an action in the request body and optional identifier for a given card request. The available actions are `update`, `set_hold`, `release_hold`, `add`, `start`, `refresh`, `abandon`, `make`, `requeue`, `complete` and `cancel`.  For the `set_hold` action, the client can optionally append a `hold_reason` field describing the reason for holding the card request.  For the `cancel` action, the client can optionally append a `cancel_reason` field describing the reason for cancelling the card request.  For the `update` action, the client can optionally append `fields` and/or `identifiers` to be updated. An `update` action without `fields` or `identifiers` refreshes the card request by updating the card request data from the data sources.  For the `make` action, the client can also append identifiers which associates the physically created cards to the card record - for example the card UID which is  pre-encoded into the card by the manufacturer.   The `complete` action returns the UUID of the created `card` entity.  ### Permissions  Principals with the `CARD_REQUEST_UPDATER` permission will be able to affect this endpoint.  Principals with the `CARD_REQUEST_CREATOR` permission are able to affect the `update`, `set_hold`, `release_hold` and `cancel` actions for card requests created by the principal.  

        :param id: A UUID string identifying this card request. (required)
        :type id: str
        :param card_request_update_request: (required)
        :type card_request_update_request: CardRequestUpdateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_update_serialize(
            id=id,
            card_request_update_request=card_request_update_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRequestUpdateResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_requests_update_serialize(
        self,
        id,
        card_request_update_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if card_request_update_request is not None:
            _body_params = card_request_update_request


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json', 
                        'application/x-www-form-urlencoded', 
                        'multipart/form-data'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='PUT',
            resource_path='/v1beta1/card-requests/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_requests_update_update(
        self,
        card_request_bulk_update_request: CardRequestBulkUpdateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CardRequestBulkUpdateResponseType:
        """Update multiple card requests

         ## Update multiple card requests.  Allows multiple card requests to be updated in one call. For large number of card requests, this endpoint will be faster than PUT-ing each update.  Updates are processed in the order they are received. The response includes the detail of the operation, the UUID of the card that was updated, and HTTP status code which would have been returned from separate PUTs. If the status code is 404, the `id` property is omitted.  ### Permissions  Principals with the `CARD_REQUEST_UPDATER` permission will be able to affect this endpoint.  

        :param card_request_bulk_update_request: (required)
        :type card_request_bulk_update_request: CardRequestBulkUpdateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_update_update_serialize(
            card_request_bulk_update_request=card_request_bulk_update_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRequestBulkUpdateResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_requests_update_update_with_http_info(
        self,
        card_request_bulk_update_request: CardRequestBulkUpdateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CardRequestBulkUpdateResponseType]:
        """Update multiple card requests

         ## Update multiple card requests.  Allows multiple card requests to be updated in one call. For large number of card requests, this endpoint will be faster than PUT-ing each update.  Updates are processed in the order they are received. The response includes the detail of the operation, the UUID of the card that was updated, and HTTP status code which would have been returned from separate PUTs. If the status code is 404, the `id` property is omitted.  ### Permissions  Principals with the `CARD_REQUEST_UPDATER` permission will be able to affect this endpoint.  

        :param card_request_bulk_update_request: (required)
        :type card_request_bulk_update_request: CardRequestBulkUpdateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_update_update_serialize(
            card_request_bulk_update_request=card_request_bulk_update_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRequestBulkUpdateResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_requests_update_update_without_preload_content(
        self,
        card_request_bulk_update_request: CardRequestBulkUpdateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update multiple card requests

         ## Update multiple card requests.  Allows multiple card requests to be updated in one call. For large number of card requests, this endpoint will be faster than PUT-ing each update.  Updates are processed in the order they are received. The response includes the detail of the operation, the UUID of the card that was updated, and HTTP status code which would have been returned from separate PUTs. If the status code is 404, the `id` property is omitted.  ### Permissions  Principals with the `CARD_REQUEST_UPDATER` permission will be able to affect this endpoint.  

        :param card_request_bulk_update_request: (required)
        :type card_request_bulk_update_request: CardRequestBulkUpdateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_requests_update_update_serialize(
            card_request_bulk_update_request=card_request_bulk_update_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRequestBulkUpdateResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_requests_update_update_serialize(
        self,
        card_request_bulk_update_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if card_request_bulk_update_request is not None:
            _body_params = card_request_bulk_update_request


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json', 
                        'application/x-www-form-urlencoded', 
                        'multipart/form-data'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='PUT',
            resource_path='/v1beta1/card-requests/update',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_card_rfid_data_config_list(
        self,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CardRFIDConfigListResponseType:
        """Returns the card RFID data configuration

        Returns the card RFID data configuration

        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_rfid_data_config_list_serialize(
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRFIDConfigListResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_card_rfid_data_config_list_with_http_info(
        self,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CardRFIDConfigListResponseType]:
        """Returns the card RFID data configuration

        Returns the card RFID data configuration

        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_rfid_data_config_list_serialize(
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRFIDConfigListResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_card_rfid_data_config_list_without_preload_content(
        self,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Returns the card RFID data configuration

        Returns the card RFID data configuration

        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_card_rfid_data_config_list_serialize(
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardRFIDConfigListResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_card_rfid_data_config_list_serialize(
        self,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/card-rfid-data-config',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_cards_back_visualization_retrieve(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card.")],
        format: Optional[StrictStr] = None,
        height: Annotated[Optional[StrictInt], Field(description="The desired height of the visualization (in pixels)")] = None,
        width: Annotated[Optional[StrictInt], Field(description="The desired width of the visualization (in pixels)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> bytearray:
        """Returns a representation of the back of this card

         ## Get card back visualization  Returns a visualization of the back of this card in BMP, PNG or SVG format.  Currently a placeholder is used to represent the barcode printed on the back of the card, this will be replaced with a valid barcode as a piece of follow-up work.  Temporary cards cannot be visualized, and will simply return a blank image.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view visualization of any card contained within the card system. Principals without this permission are only able to view the visualization for a card that they own. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param id: A UUID string identifying this card. (required)
        :type id: str
        :param format:
        :type format: str
        :param height: The desired height of the visualization (in pixels)
        :type height: int
        :param width: The desired width of the visualization (in pixels)
        :type width: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_back_visualization_retrieve_serialize(
            id=id,
            format=format,
            height=height,
            width=width,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "bytearray",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_cards_back_visualization_retrieve_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card.")],
        format: Optional[StrictStr] = None,
        height: Annotated[Optional[StrictInt], Field(description="The desired height of the visualization (in pixels)")] = None,
        width: Annotated[Optional[StrictInt], Field(description="The desired width of the visualization (in pixels)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[bytearray]:
        """Returns a representation of the back of this card

         ## Get card back visualization  Returns a visualization of the back of this card in BMP, PNG or SVG format.  Currently a placeholder is used to represent the barcode printed on the back of the card, this will be replaced with a valid barcode as a piece of follow-up work.  Temporary cards cannot be visualized, and will simply return a blank image.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view visualization of any card contained within the card system. Principals without this permission are only able to view the visualization for a card that they own. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param id: A UUID string identifying this card. (required)
        :type id: str
        :param format:
        :type format: str
        :param height: The desired height of the visualization (in pixels)
        :type height: int
        :param width: The desired width of the visualization (in pixels)
        :type width: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_back_visualization_retrieve_serialize(
            id=id,
            format=format,
            height=height,
            width=width,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "bytearray",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_cards_back_visualization_retrieve_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card.")],
        format: Optional[StrictStr] = None,
        height: Annotated[Optional[StrictInt], Field(description="The desired height of the visualization (in pixels)")] = None,
        width: Annotated[Optional[StrictInt], Field(description="The desired width of the visualization (in pixels)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Returns a representation of the back of this card

         ## Get card back visualization  Returns a visualization of the back of this card in BMP, PNG or SVG format.  Currently a placeholder is used to represent the barcode printed on the back of the card, this will be replaced with a valid barcode as a piece of follow-up work.  Temporary cards cannot be visualized, and will simply return a blank image.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view visualization of any card contained within the card system. Principals without this permission are only able to view the visualization for a card that they own. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param id: A UUID string identifying this card. (required)
        :type id: str
        :param format:
        :type format: str
        :param height: The desired height of the visualization (in pixels)
        :type height: int
        :param width: The desired width of the visualization (in pixels)
        :type width: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_back_visualization_retrieve_serialize(
            id=id,
            format=format,
            height=height,
            width=width,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "bytearray",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_cards_back_visualization_retrieve_serialize(
        self,
        id,
        format,
        height,
        width,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        if format is not None:
            
            _query_params.append(('format', format))
            
        if height is not None:
            
            _query_params.append(('height', height))
            
        if width is not None:
            
            _query_params.append(('width', width))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'image/bmp', 
                'image/png', 
                'image/svg+xml'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/cards/{id}/back-visualization',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_cards_filter_create(
        self,
        card_filter_request: CardFilterRequest,
        institution: Annotated[Optional[Annotated[str, Field(min_length=1, strict=True)]], Field(description="Filter by the institutions that cardholders belong to")] = None,
        status: Annotated[Optional[Annotated[str, Field(min_length=1, strict=True)]], Field(description="Status to filter by, if omitted cards of all statuses are returned  * `ISSUED` - Issued * `REVOKED` - Revoked * `RETURNED` - Returned * `EXPIRED` - Expired * `UNACTIVATED` - Unactivated")] = None,
        updated_at__gte: Annotated[Optional[datetime], Field(description="Filter updatedAt by IsoDateTime greater than")] = None,
        updated_at__lte: Annotated[Optional[datetime], Field(description="Filter updatedAt by IsoDateTime less than")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> PaginatedCardSummaryList:
        """Filter cards by identifiers

         ## Filter cards by Identifiers  > **WARNING!** > > A barcode identifier (`barcode.v1.card.university.identifiers.cam.ac.uk`) may be associated with more than one user. See `Known Issues` for more details.  Returns the cards related to the given batch of identifiers. This is useful for finding a set of cards based on a batch of entities from another system. For example, finding cards for members of a group in Lookup can be achieved by first fetching all members of the group and their crsids from Lookup and then using this endpoint to find all cards based on those crsids.  Identifiers should be provided in the format `<value>@<scheme>`, but if the scheme is not provided the scheme shall be assumed to be `person.crs.identifiers.uis.cam.ac.uk`. See above for the list of supported schemes.  __Note__: the number of identifiers which can be sent in each request is limited to 50, if more that 50 unique identifiers are sent in a single request a `400` error response will be returned. If cards need to be filtered by more than 50 identifiers, multiple request should be made with the identifiers split into batches of 50.  A `status` to filter cards can optionally be included in the body or as a query param. If not included cards of all statuses are returned.  Although this endpoint uses the `POST` method, no data is created. `POST` is used to allow the set of identifiers to be provided in the body and therefore avoid problems caused by query-string length limits.  This endpoint returns a paginated response object (as described above), but will not actually perform pagination due to the overall limit on the number of identifiers that can be queried by. Therefore the `next` and `previous` fields will always be `null` and the `page_size` and `cursor` query parameters will not be honoured.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to filter all cards contained within the card system. Without this permission only cards owned by the authenticated principal will be returned. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param card_filter_request: (required)
        :type card_filter_request: CardFilterRequest
        :param institution: Filter by the institutions that cardholders belong to
        :type institution: str
        :param status: Status to filter by, if omitted cards of all statuses are returned  * `ISSUED` - Issued * `REVOKED` - Revoked * `RETURNED` - Returned * `EXPIRED` - Expired * `UNACTIVATED` - Unactivated
        :type status: str
        :param updated_at__gte: Filter updatedAt by IsoDateTime greater than
        :type updated_at__gte: datetime
        :param updated_at__lte: Filter updatedAt by IsoDateTime less than
        :type updated_at__lte: datetime
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_filter_create_serialize(
            card_filter_request=card_filter_request,
            institution=institution,
            status=status,
            updated_at__gte=updated_at__gte,
            updated_at__lte=updated_at__lte,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCardSummaryList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_cards_filter_create_with_http_info(
        self,
        card_filter_request: CardFilterRequest,
        institution: Annotated[Optional[Annotated[str, Field(min_length=1, strict=True)]], Field(description="Filter by the institutions that cardholders belong to")] = None,
        status: Annotated[Optional[Annotated[str, Field(min_length=1, strict=True)]], Field(description="Status to filter by, if omitted cards of all statuses are returned  * `ISSUED` - Issued * `REVOKED` - Revoked * `RETURNED` - Returned * `EXPIRED` - Expired * `UNACTIVATED` - Unactivated")] = None,
        updated_at__gte: Annotated[Optional[datetime], Field(description="Filter updatedAt by IsoDateTime greater than")] = None,
        updated_at__lte: Annotated[Optional[datetime], Field(description="Filter updatedAt by IsoDateTime less than")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[PaginatedCardSummaryList]:
        """Filter cards by identifiers

         ## Filter cards by Identifiers  > **WARNING!** > > A barcode identifier (`barcode.v1.card.university.identifiers.cam.ac.uk`) may be associated with more than one user. See `Known Issues` for more details.  Returns the cards related to the given batch of identifiers. This is useful for finding a set of cards based on a batch of entities from another system. For example, finding cards for members of a group in Lookup can be achieved by first fetching all members of the group and their crsids from Lookup and then using this endpoint to find all cards based on those crsids.  Identifiers should be provided in the format `<value>@<scheme>`, but if the scheme is not provided the scheme shall be assumed to be `person.crs.identifiers.uis.cam.ac.uk`. See above for the list of supported schemes.  __Note__: the number of identifiers which can be sent in each request is limited to 50, if more that 50 unique identifiers are sent in a single request a `400` error response will be returned. If cards need to be filtered by more than 50 identifiers, multiple request should be made with the identifiers split into batches of 50.  A `status` to filter cards can optionally be included in the body or as a query param. If not included cards of all statuses are returned.  Although this endpoint uses the `POST` method, no data is created. `POST` is used to allow the set of identifiers to be provided in the body and therefore avoid problems caused by query-string length limits.  This endpoint returns a paginated response object (as described above), but will not actually perform pagination due to the overall limit on the number of identifiers that can be queried by. Therefore the `next` and `previous` fields will always be `null` and the `page_size` and `cursor` query parameters will not be honoured.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to filter all cards contained within the card system. Without this permission only cards owned by the authenticated principal will be returned. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param card_filter_request: (required)
        :type card_filter_request: CardFilterRequest
        :param institution: Filter by the institutions that cardholders belong to
        :type institution: str
        :param status: Status to filter by, if omitted cards of all statuses are returned  * `ISSUED` - Issued * `REVOKED` - Revoked * `RETURNED` - Returned * `EXPIRED` - Expired * `UNACTIVATED` - Unactivated
        :type status: str
        :param updated_at__gte: Filter updatedAt by IsoDateTime greater than
        :type updated_at__gte: datetime
        :param updated_at__lte: Filter updatedAt by IsoDateTime less than
        :type updated_at__lte: datetime
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_filter_create_serialize(
            card_filter_request=card_filter_request,
            institution=institution,
            status=status,
            updated_at__gte=updated_at__gte,
            updated_at__lte=updated_at__lte,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCardSummaryList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_cards_filter_create_without_preload_content(
        self,
        card_filter_request: CardFilterRequest,
        institution: Annotated[Optional[Annotated[str, Field(min_length=1, strict=True)]], Field(description="Filter by the institutions that cardholders belong to")] = None,
        status: Annotated[Optional[Annotated[str, Field(min_length=1, strict=True)]], Field(description="Status to filter by, if omitted cards of all statuses are returned  * `ISSUED` - Issued * `REVOKED` - Revoked * `RETURNED` - Returned * `EXPIRED` - Expired * `UNACTIVATED` - Unactivated")] = None,
        updated_at__gte: Annotated[Optional[datetime], Field(description="Filter updatedAt by IsoDateTime greater than")] = None,
        updated_at__lte: Annotated[Optional[datetime], Field(description="Filter updatedAt by IsoDateTime less than")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Filter cards by identifiers

         ## Filter cards by Identifiers  > **WARNING!** > > A barcode identifier (`barcode.v1.card.university.identifiers.cam.ac.uk`) may be associated with more than one user. See `Known Issues` for more details.  Returns the cards related to the given batch of identifiers. This is useful for finding a set of cards based on a batch of entities from another system. For example, finding cards for members of a group in Lookup can be achieved by first fetching all members of the group and their crsids from Lookup and then using this endpoint to find all cards based on those crsids.  Identifiers should be provided in the format `<value>@<scheme>`, but if the scheme is not provided the scheme shall be assumed to be `person.crs.identifiers.uis.cam.ac.uk`. See above for the list of supported schemes.  __Note__: the number of identifiers which can be sent in each request is limited to 50, if more that 50 unique identifiers are sent in a single request a `400` error response will be returned. If cards need to be filtered by more than 50 identifiers, multiple request should be made with the identifiers split into batches of 50.  A `status` to filter cards can optionally be included in the body or as a query param. If not included cards of all statuses are returned.  Although this endpoint uses the `POST` method, no data is created. `POST` is used to allow the set of identifiers to be provided in the body and therefore avoid problems caused by query-string length limits.  This endpoint returns a paginated response object (as described above), but will not actually perform pagination due to the overall limit on the number of identifiers that can be queried by. Therefore the `next` and `previous` fields will always be `null` and the `page_size` and `cursor` query parameters will not be honoured.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to filter all cards contained within the card system. Without this permission only cards owned by the authenticated principal will be returned. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param card_filter_request: (required)
        :type card_filter_request: CardFilterRequest
        :param institution: Filter by the institutions that cardholders belong to
        :type institution: str
        :param status: Status to filter by, if omitted cards of all statuses are returned  * `ISSUED` - Issued * `REVOKED` - Revoked * `RETURNED` - Returned * `EXPIRED` - Expired * `UNACTIVATED` - Unactivated
        :type status: str
        :param updated_at__gte: Filter updatedAt by IsoDateTime greater than
        :type updated_at__gte: datetime
        :param updated_at__lte: Filter updatedAt by IsoDateTime less than
        :type updated_at__lte: datetime
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_filter_create_serialize(
            card_filter_request=card_filter_request,
            institution=institution,
            status=status,
            updated_at__gte=updated_at__gte,
            updated_at__lte=updated_at__lte,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCardSummaryList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_cards_filter_create_serialize(
        self,
        card_filter_request,
        institution,
        status,
        updated_at__gte,
        updated_at__lte,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if institution is not None:
            
            _query_params.append(('institution', institution))
            
        if status is not None:
            
            _query_params.append(('status', status))
            
        if updated_at__gte is not None:
            if isinstance(updated_at__gte, datetime):
                _query_params.append(
                    (
                        'updated_at__gte',
                        updated_at__gte.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('updated_at__gte', updated_at__gte))
            
        if updated_at__lte is not None:
            if isinstance(updated_at__lte, datetime):
                _query_params.append(
                    (
                        'updated_at__lte',
                        updated_at__lte.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('updated_at__lte', updated_at__lte))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if card_filter_request is not None:
            _body_params = card_filter_request


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json', 
                        'application/x-www-form-urlencoded', 
                        'multipart/form-data'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/v1beta1/cards/filter',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_cards_front_visualization_retrieve(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card.")],
        format: Optional[StrictStr] = None,
        height: Annotated[Optional[StrictInt], Field(description="The desired height of the visualization (in pixels)")] = None,
        width: Annotated[Optional[StrictInt], Field(description="The desired width of the visualization (in pixels)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> bytearray:
        """Returns a representation of the front of this card

         ## Get card front visualization  Returns a visualization of the front of this card in BMP, PNG or SVG format. Makes use of the Photo API to fetch the photo of the cardholder used on this card. In cases where this card makes use of an out-of-date photo of the cardholder imported from the legacy card system, the Photo may not be available, in which case a placeholder is displayed.  Temporary cards cannot be visualized, and will simply return a blank image.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view visualization of any card contained within the card system. Principals without this permission are only able to view the visualization for a card that they own. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param id: A UUID string identifying this card. (required)
        :type id: str
        :param format:
        :type format: str
        :param height: The desired height of the visualization (in pixels)
        :type height: int
        :param width: The desired width of the visualization (in pixels)
        :type width: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_front_visualization_retrieve_serialize(
            id=id,
            format=format,
            height=height,
            width=width,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "bytearray",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_cards_front_visualization_retrieve_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card.")],
        format: Optional[StrictStr] = None,
        height: Annotated[Optional[StrictInt], Field(description="The desired height of the visualization (in pixels)")] = None,
        width: Annotated[Optional[StrictInt], Field(description="The desired width of the visualization (in pixels)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[bytearray]:
        """Returns a representation of the front of this card

         ## Get card front visualization  Returns a visualization of the front of this card in BMP, PNG or SVG format. Makes use of the Photo API to fetch the photo of the cardholder used on this card. In cases where this card makes use of an out-of-date photo of the cardholder imported from the legacy card system, the Photo may not be available, in which case a placeholder is displayed.  Temporary cards cannot be visualized, and will simply return a blank image.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view visualization of any card contained within the card system. Principals without this permission are only able to view the visualization for a card that they own. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param id: A UUID string identifying this card. (required)
        :type id: str
        :param format:
        :type format: str
        :param height: The desired height of the visualization (in pixels)
        :type height: int
        :param width: The desired width of the visualization (in pixels)
        :type width: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_front_visualization_retrieve_serialize(
            id=id,
            format=format,
            height=height,
            width=width,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "bytearray",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_cards_front_visualization_retrieve_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card.")],
        format: Optional[StrictStr] = None,
        height: Annotated[Optional[StrictInt], Field(description="The desired height of the visualization (in pixels)")] = None,
        width: Annotated[Optional[StrictInt], Field(description="The desired width of the visualization (in pixels)")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Returns a representation of the front of this card

         ## Get card front visualization  Returns a visualization of the front of this card in BMP, PNG or SVG format. Makes use of the Photo API to fetch the photo of the cardholder used on this card. In cases where this card makes use of an out-of-date photo of the cardholder imported from the legacy card system, the Photo may not be available, in which case a placeholder is displayed.  Temporary cards cannot be visualized, and will simply return a blank image.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view visualization of any card contained within the card system. Principals without this permission are only able to view the visualization for a card that they own. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param id: A UUID string identifying this card. (required)
        :type id: str
        :param format:
        :type format: str
        :param height: The desired height of the visualization (in pixels)
        :type height: int
        :param width: The desired width of the visualization (in pixels)
        :type width: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_front_visualization_retrieve_serialize(
            id=id,
            format=format,
            height=height,
            width=width,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "bytearray",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_cards_front_visualization_retrieve_serialize(
        self,
        id,
        format,
        height,
        width,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        if format is not None:
            
            _query_params.append(('format', format))
            
        if height is not None:
            
            _query_params.append(('height', height))
            
        if width is not None:
            
            _query_params.append(('width', width))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'image/bmp', 
                'image/png', 
                'image/svg+xml'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/cards/{id}/front-visualization',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_cards_list(
        self,
        card_type: Annotated[Optional[StrictStr], Field(description="Filter by the type of card  * `MIFARE_PERSONAL` - Personal * `MIFARE_TEMPORARY` - Temporary")] = None,
        created_at__gte: Optional[datetime] = None,
        created_at__lte: Optional[datetime] = None,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        expires_at__gte: Optional[datetime] = None,
        expires_at__isnull: Optional[StrictBool] = None,
        expires_at__lte: Optional[datetime] = None,
        identifier: Annotated[Optional[StrictStr], Field(description="Filter cards by an identifier in the format {value}@{scheme}")] = None,
        institution: Annotated[Optional[StrictStr], Field(description="Institution id")] = None,
        issued_at__gte: Optional[datetime] = None,
        issued_at__isnull: Optional[StrictBool] = None,
        issued_at__lte: Optional[datetime] = None,
        originating_card_request: Annotated[Optional[StrictStr], Field(description="Originating CardRequest UUID")] = None,
        originating_card_request__isnull: Optional[StrictBool] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        search: Annotated[Optional[StrictStr], Field(description="A search term.")] = None,
        status: Annotated[Optional[StrictStr], Field(description="Filter cards by their current status  * `ISSUED` - Issued * `REVOKED` - Revoked * `RETURNED` - Returned * `EXPIRED` - Expired * `UNACTIVATED` - Unactivated")] = None,
        updated_at__gte: Optional[datetime] = None,
        updated_at__lte: Optional[datetime] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> PaginatedCardSummaryList:
        """List cards

        ## List Cards  Allows current and historic University Cards to be listed.  By default (without any URL parameters included) this method will return all cards, including temporary cards and cards that have expired / been revoked.  Query parameters can be used to refine the cards that are returned. For example, to fetch cards which have been issued and are therefore currently active we can add the query parameter: `status=ISSUED`.  > **WARNING!** > > A barcode identifier (`barcode.v1.card.university.identifiers.cam.ac.uk`) may be associated with more than one user. See `Known Issues` for more details.  If we want to find Cards with a specific identifier we can specify that identifier as a query parameter as well. For example, adding the following to the query string will return all revoked cards with the mifare ID '123':  `status=REVOKED&identifier=123@<mifare id scheme>`. Identifiers should be provided in the format `<value>@<scheme>`, but if the scheme is not provided the scheme shall be assumed to be the CRSid. See above for the list of supported schemes.  In the case of querying by mifare identifier, any leading zeros within the identifier value included in the query will be ignored - so querying with `identifier=0000000123@<mifare id scheme>` and `identifier=123@<mifare id scheme>` will return the same result.  Alternately the `search` query parameter can be used to search all cards by a single identifier value regardless of the scheme of that identifier.  If cards for multiple identifiers need to be fetched, use the `/cards/filter/` endpoint documented below.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view all cards contained within the card system. Without this permission only cards owned by the authenticated principal will be returned. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param card_type: Filter by the type of card  * `MIFARE_PERSONAL` - Personal * `MIFARE_TEMPORARY` - Temporary
        :type card_type: str
        :param created_at__gte:
        :type created_at__gte: datetime
        :param created_at__lte:
        :type created_at__lte: datetime
        :param cursor: The pagination cursor value.
        :type cursor: str
        :param expires_at__gte:
        :type expires_at__gte: datetime
        :param expires_at__isnull:
        :type expires_at__isnull: bool
        :param expires_at__lte:
        :type expires_at__lte: datetime
        :param identifier: Filter cards by an identifier in the format {value}@{scheme}
        :type identifier: str
        :param institution: Institution id
        :type institution: str
        :param issued_at__gte:
        :type issued_at__gte: datetime
        :param issued_at__isnull:
        :type issued_at__isnull: bool
        :param issued_at__lte:
        :type issued_at__lte: datetime
        :param originating_card_request: Originating CardRequest UUID
        :type originating_card_request: str
        :param originating_card_request__isnull:
        :type originating_card_request__isnull: bool
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param search: A search term.
        :type search: str
        :param status: Filter cards by their current status  * `ISSUED` - Issued * `REVOKED` - Revoked * `RETURNED` - Returned * `EXPIRED` - Expired * `UNACTIVATED` - Unactivated
        :type status: str
        :param updated_at__gte:
        :type updated_at__gte: datetime
        :param updated_at__lte:
        :type updated_at__lte: datetime
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_list_serialize(
            card_type=card_type,
            created_at__gte=created_at__gte,
            created_at__lte=created_at__lte,
            cursor=cursor,
            expires_at__gte=expires_at__gte,
            expires_at__isnull=expires_at__isnull,
            expires_at__lte=expires_at__lte,
            identifier=identifier,
            institution=institution,
            issued_at__gte=issued_at__gte,
            issued_at__isnull=issued_at__isnull,
            issued_at__lte=issued_at__lte,
            originating_card_request=originating_card_request,
            originating_card_request__isnull=originating_card_request__isnull,
            page_size=page_size,
            search=search,
            status=status,
            updated_at__gte=updated_at__gte,
            updated_at__lte=updated_at__lte,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCardSummaryList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_cards_list_with_http_info(
        self,
        card_type: Annotated[Optional[StrictStr], Field(description="Filter by the type of card  * `MIFARE_PERSONAL` - Personal * `MIFARE_TEMPORARY` - Temporary")] = None,
        created_at__gte: Optional[datetime] = None,
        created_at__lte: Optional[datetime] = None,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        expires_at__gte: Optional[datetime] = None,
        expires_at__isnull: Optional[StrictBool] = None,
        expires_at__lte: Optional[datetime] = None,
        identifier: Annotated[Optional[StrictStr], Field(description="Filter cards by an identifier in the format {value}@{scheme}")] = None,
        institution: Annotated[Optional[StrictStr], Field(description="Institution id")] = None,
        issued_at__gte: Optional[datetime] = None,
        issued_at__isnull: Optional[StrictBool] = None,
        issued_at__lte: Optional[datetime] = None,
        originating_card_request: Annotated[Optional[StrictStr], Field(description="Originating CardRequest UUID")] = None,
        originating_card_request__isnull: Optional[StrictBool] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        search: Annotated[Optional[StrictStr], Field(description="A search term.")] = None,
        status: Annotated[Optional[StrictStr], Field(description="Filter cards by their current status  * `ISSUED` - Issued * `REVOKED` - Revoked * `RETURNED` - Returned * `EXPIRED` - Expired * `UNACTIVATED` - Unactivated")] = None,
        updated_at__gte: Optional[datetime] = None,
        updated_at__lte: Optional[datetime] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[PaginatedCardSummaryList]:
        """List cards

        ## List Cards  Allows current and historic University Cards to be listed.  By default (without any URL parameters included) this method will return all cards, including temporary cards and cards that have expired / been revoked.  Query parameters can be used to refine the cards that are returned. For example, to fetch cards which have been issued and are therefore currently active we can add the query parameter: `status=ISSUED`.  > **WARNING!** > > A barcode identifier (`barcode.v1.card.university.identifiers.cam.ac.uk`) may be associated with more than one user. See `Known Issues` for more details.  If we want to find Cards with a specific identifier we can specify that identifier as a query parameter as well. For example, adding the following to the query string will return all revoked cards with the mifare ID '123':  `status=REVOKED&identifier=123@<mifare id scheme>`. Identifiers should be provided in the format `<value>@<scheme>`, but if the scheme is not provided the scheme shall be assumed to be the CRSid. See above for the list of supported schemes.  In the case of querying by mifare identifier, any leading zeros within the identifier value included in the query will be ignored - so querying with `identifier=0000000123@<mifare id scheme>` and `identifier=123@<mifare id scheme>` will return the same result.  Alternately the `search` query parameter can be used to search all cards by a single identifier value regardless of the scheme of that identifier.  If cards for multiple identifiers need to be fetched, use the `/cards/filter/` endpoint documented below.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view all cards contained within the card system. Without this permission only cards owned by the authenticated principal will be returned. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param card_type: Filter by the type of card  * `MIFARE_PERSONAL` - Personal * `MIFARE_TEMPORARY` - Temporary
        :type card_type: str
        :param created_at__gte:
        :type created_at__gte: datetime
        :param created_at__lte:
        :type created_at__lte: datetime
        :param cursor: The pagination cursor value.
        :type cursor: str
        :param expires_at__gte:
        :type expires_at__gte: datetime
        :param expires_at__isnull:
        :type expires_at__isnull: bool
        :param expires_at__lte:
        :type expires_at__lte: datetime
        :param identifier: Filter cards by an identifier in the format {value}@{scheme}
        :type identifier: str
        :param institution: Institution id
        :type institution: str
        :param issued_at__gte:
        :type issued_at__gte: datetime
        :param issued_at__isnull:
        :type issued_at__isnull: bool
        :param issued_at__lte:
        :type issued_at__lte: datetime
        :param originating_card_request: Originating CardRequest UUID
        :type originating_card_request: str
        :param originating_card_request__isnull:
        :type originating_card_request__isnull: bool
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param search: A search term.
        :type search: str
        :param status: Filter cards by their current status  * `ISSUED` - Issued * `REVOKED` - Revoked * `RETURNED` - Returned * `EXPIRED` - Expired * `UNACTIVATED` - Unactivated
        :type status: str
        :param updated_at__gte:
        :type updated_at__gte: datetime
        :param updated_at__lte:
        :type updated_at__lte: datetime
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_list_serialize(
            card_type=card_type,
            created_at__gte=created_at__gte,
            created_at__lte=created_at__lte,
            cursor=cursor,
            expires_at__gte=expires_at__gte,
            expires_at__isnull=expires_at__isnull,
            expires_at__lte=expires_at__lte,
            identifier=identifier,
            institution=institution,
            issued_at__gte=issued_at__gte,
            issued_at__isnull=issued_at__isnull,
            issued_at__lte=issued_at__lte,
            originating_card_request=originating_card_request,
            originating_card_request__isnull=originating_card_request__isnull,
            page_size=page_size,
            search=search,
            status=status,
            updated_at__gte=updated_at__gte,
            updated_at__lte=updated_at__lte,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCardSummaryList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_cards_list_without_preload_content(
        self,
        card_type: Annotated[Optional[StrictStr], Field(description="Filter by the type of card  * `MIFARE_PERSONAL` - Personal * `MIFARE_TEMPORARY` - Temporary")] = None,
        created_at__gte: Optional[datetime] = None,
        created_at__lte: Optional[datetime] = None,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        expires_at__gte: Optional[datetime] = None,
        expires_at__isnull: Optional[StrictBool] = None,
        expires_at__lte: Optional[datetime] = None,
        identifier: Annotated[Optional[StrictStr], Field(description="Filter cards by an identifier in the format {value}@{scheme}")] = None,
        institution: Annotated[Optional[StrictStr], Field(description="Institution id")] = None,
        issued_at__gte: Optional[datetime] = None,
        issued_at__isnull: Optional[StrictBool] = None,
        issued_at__lte: Optional[datetime] = None,
        originating_card_request: Annotated[Optional[StrictStr], Field(description="Originating CardRequest UUID")] = None,
        originating_card_request__isnull: Optional[StrictBool] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        search: Annotated[Optional[StrictStr], Field(description="A search term.")] = None,
        status: Annotated[Optional[StrictStr], Field(description="Filter cards by their current status  * `ISSUED` - Issued * `REVOKED` - Revoked * `RETURNED` - Returned * `EXPIRED` - Expired * `UNACTIVATED` - Unactivated")] = None,
        updated_at__gte: Optional[datetime] = None,
        updated_at__lte: Optional[datetime] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """List cards

        ## List Cards  Allows current and historic University Cards to be listed.  By default (without any URL parameters included) this method will return all cards, including temporary cards and cards that have expired / been revoked.  Query parameters can be used to refine the cards that are returned. For example, to fetch cards which have been issued and are therefore currently active we can add the query parameter: `status=ISSUED`.  > **WARNING!** > > A barcode identifier (`barcode.v1.card.university.identifiers.cam.ac.uk`) may be associated with more than one user. See `Known Issues` for more details.  If we want to find Cards with a specific identifier we can specify that identifier as a query parameter as well. For example, adding the following to the query string will return all revoked cards with the mifare ID '123':  `status=REVOKED&identifier=123@<mifare id scheme>`. Identifiers should be provided in the format `<value>@<scheme>`, but if the scheme is not provided the scheme shall be assumed to be the CRSid. See above for the list of supported schemes.  In the case of querying by mifare identifier, any leading zeros within the identifier value included in the query will be ignored - so querying with `identifier=0000000123@<mifare id scheme>` and `identifier=123@<mifare id scheme>` will return the same result.  Alternately the `search` query parameter can be used to search all cards by a single identifier value regardless of the scheme of that identifier.  If cards for multiple identifiers need to be fetched, use the `/cards/filter/` endpoint documented below.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view all cards contained within the card system. Without this permission only cards owned by the authenticated principal will be returned. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param card_type: Filter by the type of card  * `MIFARE_PERSONAL` - Personal * `MIFARE_TEMPORARY` - Temporary
        :type card_type: str
        :param created_at__gte:
        :type created_at__gte: datetime
        :param created_at__lte:
        :type created_at__lte: datetime
        :param cursor: The pagination cursor value.
        :type cursor: str
        :param expires_at__gte:
        :type expires_at__gte: datetime
        :param expires_at__isnull:
        :type expires_at__isnull: bool
        :param expires_at__lte:
        :type expires_at__lte: datetime
        :param identifier: Filter cards by an identifier in the format {value}@{scheme}
        :type identifier: str
        :param institution: Institution id
        :type institution: str
        :param issued_at__gte:
        :type issued_at__gte: datetime
        :param issued_at__isnull:
        :type issued_at__isnull: bool
        :param issued_at__lte:
        :type issued_at__lte: datetime
        :param originating_card_request: Originating CardRequest UUID
        :type originating_card_request: str
        :param originating_card_request__isnull:
        :type originating_card_request__isnull: bool
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param search: A search term.
        :type search: str
        :param status: Filter cards by their current status  * `ISSUED` - Issued * `REVOKED` - Revoked * `RETURNED` - Returned * `EXPIRED` - Expired * `UNACTIVATED` - Unactivated
        :type status: str
        :param updated_at__gte:
        :type updated_at__gte: datetime
        :param updated_at__lte:
        :type updated_at__lte: datetime
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_list_serialize(
            card_type=card_type,
            created_at__gte=created_at__gte,
            created_at__lte=created_at__lte,
            cursor=cursor,
            expires_at__gte=expires_at__gte,
            expires_at__isnull=expires_at__isnull,
            expires_at__lte=expires_at__lte,
            identifier=identifier,
            institution=institution,
            issued_at__gte=issued_at__gte,
            issued_at__isnull=issued_at__isnull,
            issued_at__lte=issued_at__lte,
            originating_card_request=originating_card_request,
            originating_card_request__isnull=originating_card_request__isnull,
            page_size=page_size,
            search=search,
            status=status,
            updated_at__gte=updated_at__gte,
            updated_at__lte=updated_at__lte,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCardSummaryList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_cards_list_serialize(
        self,
        card_type,
        created_at__gte,
        created_at__lte,
        cursor,
        expires_at__gte,
        expires_at__isnull,
        expires_at__lte,
        identifier,
        institution,
        issued_at__gte,
        issued_at__isnull,
        issued_at__lte,
        originating_card_request,
        originating_card_request__isnull,
        page_size,
        search,
        status,
        updated_at__gte,
        updated_at__lte,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if card_type is not None:
            
            _query_params.append(('card_type', card_type))
            
        if created_at__gte is not None:
            if isinstance(created_at__gte, datetime):
                _query_params.append(
                    (
                        'created_at__gte',
                        created_at__gte.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('created_at__gte', created_at__gte))
            
        if created_at__lte is not None:
            if isinstance(created_at__lte, datetime):
                _query_params.append(
                    (
                        'created_at__lte',
                        created_at__lte.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('created_at__lte', created_at__lte))
            
        if cursor is not None:
            
            _query_params.append(('cursor', cursor))
            
        if expires_at__gte is not None:
            if isinstance(expires_at__gte, datetime):
                _query_params.append(
                    (
                        'expires_at__gte',
                        expires_at__gte.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('expires_at__gte', expires_at__gte))
            
        if expires_at__isnull is not None:
            
            _query_params.append(('expires_at__isnull', expires_at__isnull))
            
        if expires_at__lte is not None:
            if isinstance(expires_at__lte, datetime):
                _query_params.append(
                    (
                        'expires_at__lte',
                        expires_at__lte.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('expires_at__lte', expires_at__lte))
            
        if identifier is not None:
            
            _query_params.append(('identifier', identifier))
            
        if institution is not None:
            
            _query_params.append(('institution', institution))
            
        if issued_at__gte is not None:
            if isinstance(issued_at__gte, datetime):
                _query_params.append(
                    (
                        'issued_at__gte',
                        issued_at__gte.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('issued_at__gte', issued_at__gte))
            
        if issued_at__isnull is not None:
            
            _query_params.append(('issued_at__isnull', issued_at__isnull))
            
        if issued_at__lte is not None:
            if isinstance(issued_at__lte, datetime):
                _query_params.append(
                    (
                        'issued_at__lte',
                        issued_at__lte.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('issued_at__lte', issued_at__lte))
            
        if originating_card_request is not None:
            
            _query_params.append(('originating_card_request', originating_card_request))
            
        if originating_card_request__isnull is not None:
            
            _query_params.append(('originating_card_request__isnull', originating_card_request__isnull))
            
        if page_size is not None:
            
            _query_params.append(('page_size', page_size))
            
        if search is not None:
            
            _query_params.append(('search', search))
            
        if status is not None:
            
            _query_params.append(('status', status))
            
        if updated_at__gte is not None:
            if isinstance(updated_at__gte, datetime):
                _query_params.append(
                    (
                        'updated_at__gte',
                        updated_at__gte.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('updated_at__gte', updated_at__gte))
            
        if updated_at__lte is not None:
            if isinstance(updated_at__lte, datetime):
                _query_params.append(
                    (
                        'updated_at__lte',
                        updated_at__lte.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('updated_at__lte', updated_at__lte))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/cards',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_cards_retrieve(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> Card:
        """Get card detail

         ## Get Card Detail  Allows the detail of a single Card to be retrieved by ID. The Card entity returned contains the same information as presented in the filter and list card operations above, but also contains an array of `cardNotes` containing notes made by administrator users related to the current card.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view the card detail of any card contained within the card system. Principals without this permission are only able to view the card detail for a card that they own. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param id: A UUID string identifying this card. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Card",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_cards_retrieve_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[Card]:
        """Get card detail

         ## Get Card Detail  Allows the detail of a single Card to be retrieved by ID. The Card entity returned contains the same information as presented in the filter and list card operations above, but also contains an array of `cardNotes` containing notes made by administrator users related to the current card.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view the card detail of any card contained within the card system. Principals without this permission are only able to view the card detail for a card that they own. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param id: A UUID string identifying this card. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Card",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_cards_retrieve_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get card detail

         ## Get Card Detail  Allows the detail of a single Card to be retrieved by ID. The Card entity returned contains the same information as presented in the filter and list card operations above, but also contains an array of `cardNotes` containing notes made by administrator users related to the current card.  ### Permissions  Principals with the `CARD_DATA_READERS` permission are able to view the card detail of any card contained within the card system. Principals without this permission are only able to view the card detail for a card that they own. Ownership is determined based on the principal's identifier matching an identifier contained within a given card record.  

        :param id: A UUID string identifying this card. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Card",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_cards_retrieve_serialize(
        self,
        id,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/cards/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_cards_update(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card.")],
        card_update_request: CardUpdateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CardUpdateResponseType:
        """Update the card

         ## Update the card  This method allows a client to submit an action in the request body and optional note for a given card. The allowed action is `cancel`.  The `cancel` action cancels the card. The client can optionally append a `note` describing the reason for cancelling the card.  The `refresh` action refreshes the card state. If the card is UNACTIVATED and the cardholder does not have an ISSUED card, the card state will be updated to ISSUED.  ### Permissions  Principals with the `CARD_UPDATER` permission will be able to affect this endpoint.  

        :param id: A UUID string identifying this card. (required)
        :type id: str
        :param card_update_request: (required)
        :type card_update_request: CardUpdateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_update_serialize(
            id=id,
            card_update_request=card_update_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardUpdateResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_cards_update_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card.")],
        card_update_request: CardUpdateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CardUpdateResponseType]:
        """Update the card

         ## Update the card  This method allows a client to submit an action in the request body and optional note for a given card. The allowed action is `cancel`.  The `cancel` action cancels the card. The client can optionally append a `note` describing the reason for cancelling the card.  The `refresh` action refreshes the card state. If the card is UNACTIVATED and the cardholder does not have an ISSUED card, the card state will be updated to ISSUED.  ### Permissions  Principals with the `CARD_UPDATER` permission will be able to affect this endpoint.  

        :param id: A UUID string identifying this card. (required)
        :type id: str
        :param card_update_request: (required)
        :type card_update_request: CardUpdateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_update_serialize(
            id=id,
            card_update_request=card_update_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardUpdateResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_cards_update_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this card.")],
        card_update_request: CardUpdateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update the card

         ## Update the card  This method allows a client to submit an action in the request body and optional note for a given card. The allowed action is `cancel`.  The `cancel` action cancels the card. The client can optionally append a `note` describing the reason for cancelling the card.  The `refresh` action refreshes the card state. If the card is UNACTIVATED and the cardholder does not have an ISSUED card, the card state will be updated to ISSUED.  ### Permissions  Principals with the `CARD_UPDATER` permission will be able to affect this endpoint.  

        :param id: A UUID string identifying this card. (required)
        :type id: str
        :param card_update_request: (required)
        :type card_update_request: CardUpdateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_update_serialize(
            id=id,
            card_update_request=card_update_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardUpdateResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_cards_update_serialize(
        self,
        id,
        card_update_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if card_update_request is not None:
            _body_params = card_update_request


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json', 
                        'application/x-www-form-urlencoded', 
                        'multipart/form-data'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='PUT',
            resource_path='/v1beta1/cards/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_cards_update_update(
        self,
        card_bulk_update_request: CardBulkUpdateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CardBulkUpdateResponseType:
        """Update a set of cards

         ## Update multiple cards  Allows multiple cards to be updated in one call. For large number of cards, this endpoint will be faster than PUT-ing each update.  Updates are processed in the order they are received. The response includes the detail of the operation, the UUID of the card that was updated, and HTTP status code which would have been returned from separate PUTs. If the status code is 404, the `id` property is omitted.  ### Permissions  Principals with the `CARD_UPDATER` permission will be able to affect this endpoint.  

        :param card_bulk_update_request: (required)
        :type card_bulk_update_request: CardBulkUpdateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_update_update_serialize(
            card_bulk_update_request=card_bulk_update_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardBulkUpdateResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_cards_update_update_with_http_info(
        self,
        card_bulk_update_request: CardBulkUpdateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CardBulkUpdateResponseType]:
        """Update a set of cards

         ## Update multiple cards  Allows multiple cards to be updated in one call. For large number of cards, this endpoint will be faster than PUT-ing each update.  Updates are processed in the order they are received. The response includes the detail of the operation, the UUID of the card that was updated, and HTTP status code which would have been returned from separate PUTs. If the status code is 404, the `id` property is omitted.  ### Permissions  Principals with the `CARD_UPDATER` permission will be able to affect this endpoint.  

        :param card_bulk_update_request: (required)
        :type card_bulk_update_request: CardBulkUpdateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_update_update_serialize(
            card_bulk_update_request=card_bulk_update_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardBulkUpdateResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_cards_update_update_without_preload_content(
        self,
        card_bulk_update_request: CardBulkUpdateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update a set of cards

         ## Update multiple cards  Allows multiple cards to be updated in one call. For large number of cards, this endpoint will be faster than PUT-ing each update.  Updates are processed in the order they are received. The response includes the detail of the operation, the UUID of the card that was updated, and HTTP status code which would have been returned from separate PUTs. If the status code is 404, the `id` property is omitted.  ### Permissions  Principals with the `CARD_UPDATER` permission will be able to affect this endpoint.  

        :param card_bulk_update_request: (required)
        :type card_bulk_update_request: CardBulkUpdateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_cards_update_update_serialize(
            card_bulk_update_request=card_bulk_update_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CardBulkUpdateResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_cards_update_update_serialize(
        self,
        card_bulk_update_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if card_bulk_update_request is not None:
            _body_params = card_bulk_update_request


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json', 
                        'application/x-www-form-urlencoded', 
                        'multipart/form-data'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='PUT',
            resource_path='/v1beta1/cards/update',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_college_institution_ids_list(
        self,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CollegeInstituionsIdsListResponseType:
        """List college and institution ids

         ## List College Institution Ids  Returns a list of the college institution ids used to set the card request scarf-code.  ### Permissions  Only principals with the `CARD_DATA_READERS` permission are able to list college institution ids.  

        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_college_institution_ids_list_serialize(
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CollegeInstituionsIdsListResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_college_institution_ids_list_with_http_info(
        self,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CollegeInstituionsIdsListResponseType]:
        """List college and institution ids

         ## List College Institution Ids  Returns a list of the college institution ids used to set the card request scarf-code.  ### Permissions  Only principals with the `CARD_DATA_READERS` permission are able to list college institution ids.  

        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_college_institution_ids_list_serialize(
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CollegeInstituionsIdsListResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_college_institution_ids_list_without_preload_content(
        self,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """List college and institution ids

         ## List College Institution Ids  Returns a list of the college institution ids used to set the card request scarf-code.  ### Permissions  Only principals with the `CARD_DATA_READERS` permission are able to list college institution ids.  

        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_college_institution_ids_list_serialize(
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CollegeInstituionsIdsListResponseType",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_college_institution_ids_list_serialize(
        self,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/college-institution-ids',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_discontinued_identifiers_create(
        self,
        discontinued_identifier_create_request: DiscontinuedIdentifierCreateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> DiscontinuedIdentifier:
        """Creates a discontinued identifier

        Creates a discontinued identifier, optionally linking it to a permitted identifier and notes

        :param discontinued_identifier_create_request: (required)
        :type discontinued_identifier_create_request: DiscontinuedIdentifierCreateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_discontinued_identifiers_create_serialize(
            discontinued_identifier_create_request=discontinued_identifier_create_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '201': "DiscontinuedIdentifier",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_discontinued_identifiers_create_with_http_info(
        self,
        discontinued_identifier_create_request: DiscontinuedIdentifierCreateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[DiscontinuedIdentifier]:
        """Creates a discontinued identifier

        Creates a discontinued identifier, optionally linking it to a permitted identifier and notes

        :param discontinued_identifier_create_request: (required)
        :type discontinued_identifier_create_request: DiscontinuedIdentifierCreateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_discontinued_identifiers_create_serialize(
            discontinued_identifier_create_request=discontinued_identifier_create_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '201': "DiscontinuedIdentifier",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_discontinued_identifiers_create_without_preload_content(
        self,
        discontinued_identifier_create_request: DiscontinuedIdentifierCreateRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Creates a discontinued identifier

        Creates a discontinued identifier, optionally linking it to a permitted identifier and notes

        :param discontinued_identifier_create_request: (required)
        :type discontinued_identifier_create_request: DiscontinuedIdentifierCreateRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_discontinued_identifiers_create_serialize(
            discontinued_identifier_create_request=discontinued_identifier_create_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '201': "DiscontinuedIdentifier",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_discontinued_identifiers_create_serialize(
        self,
        discontinued_identifier_create_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if discontinued_identifier_create_request is not None:
            _body_params = discontinued_identifier_create_request


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json', 
                        'application/x-www-form-urlencoded', 
                        'multipart/form-data'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/v1beta1/discontinued-identifiers',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_discontinued_identifiers_destroy(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this discontinued identifier.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> DiscontinuedIdentifier:
        """Deletes a discontinued identifier

        Removes a discontinued identifier from the list of identifiers. This is for use by admins to correct erroneously added discontinued identifiers only.

        :param id: A UUID string identifying this discontinued identifier. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_discontinued_identifiers_destroy_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "DiscontinuedIdentifier",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_discontinued_identifiers_destroy_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this discontinued identifier.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[DiscontinuedIdentifier]:
        """Deletes a discontinued identifier

        Removes a discontinued identifier from the list of identifiers. This is for use by admins to correct erroneously added discontinued identifiers only.

        :param id: A UUID string identifying this discontinued identifier. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_discontinued_identifiers_destroy_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "DiscontinuedIdentifier",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_discontinued_identifiers_destroy_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this discontinued identifier.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Deletes a discontinued identifier

        Removes a discontinued identifier from the list of identifiers. This is for use by admins to correct erroneously added discontinued identifiers only.

        :param id: A UUID string identifying this discontinued identifier. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_discontinued_identifiers_destroy_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "DiscontinuedIdentifier",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_discontinued_identifiers_destroy_serialize(
        self,
        id,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='DELETE',
            resource_path='/v1beta1/discontinued-identifiers/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_discontinued_identifiers_list(
        self,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> PaginatedDiscontinuedIdentifierList:
        """List discontinued identifiers

        Returns a list of discontinued identifiers

        :param cursor: The pagination cursor value.
        :type cursor: str
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_discontinued_identifiers_list_serialize(
            cursor=cursor,
            page_size=page_size,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedDiscontinuedIdentifierList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_discontinued_identifiers_list_with_http_info(
        self,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[PaginatedDiscontinuedIdentifierList]:
        """List discontinued identifiers

        Returns a list of discontinued identifiers

        :param cursor: The pagination cursor value.
        :type cursor: str
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_discontinued_identifiers_list_serialize(
            cursor=cursor,
            page_size=page_size,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedDiscontinuedIdentifierList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_discontinued_identifiers_list_without_preload_content(
        self,
        cursor: Annotated[Optional[StrictStr], Field(description="The pagination cursor value.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="Number of results to return per page.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """List discontinued identifiers

        Returns a list of discontinued identifiers

        :param cursor: The pagination cursor value.
        :type cursor: str
        :param page_size: Number of results to return per page.
        :type page_size: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_discontinued_identifiers_list_serialize(
            cursor=cursor,
            page_size=page_size,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedDiscontinuedIdentifierList",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_discontinued_identifiers_list_serialize(
        self,
        cursor,
        page_size,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if cursor is not None:
            
            _query_params.append(('cursor', cursor))
            
        if page_size is not None:
            
            _query_params.append(('page_size', page_size))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/discontinued-identifiers',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v1beta1_discontinued_identifiers_retrieve(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this discontinued identifier.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> DiscontinuedIdentifier:
        """Get discontinued identifier detail

        Returns a single discontinued identifier by id

        :param id: A UUID string identifying this discontinued identifier. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_discontinued_identifiers_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "DiscontinuedIdentifier",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v1beta1_discontinued_identifiers_retrieve_with_http_info(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this discontinued identifier.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[DiscontinuedIdentifier]:
        """Get discontinued identifier detail

        Returns a single discontinued identifier by id

        :param id: A UUID string identifying this discontinued identifier. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_discontinued_identifiers_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "DiscontinuedIdentifier",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v1beta1_discontinued_identifiers_retrieve_without_preload_content(
        self,
        id: Annotated[str, Field(strict=True, description="A UUID string identifying this discontinued identifier.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get discontinued identifier detail

        Returns a single discontinued identifier by id

        :param id: A UUID string identifying this discontinued identifier. (required)
        :type id: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v1beta1_discontinued_identifiers_retrieve_serialize(
            id=id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "DiscontinuedIdentifier",
            '400': "BadRequest",
            '401': "Unauthorized",
            '403': "Forbidden",
            '404': "NotFound",
            '500': "InternalServerError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v1beta1_discontinued_identifiers_retrieve_serialize(
        self,
        id,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'apiGatewayAuthorizationCodeSecurityScheme', 
            'apiGatewayClientCredentialsSecurityScheme'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1beta1/discontinued-identifiers/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )


