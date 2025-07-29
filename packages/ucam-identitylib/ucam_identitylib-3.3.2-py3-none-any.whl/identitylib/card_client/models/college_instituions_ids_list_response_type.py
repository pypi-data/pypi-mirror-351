# coding: utf-8

"""
    University Card API

     # Card Specification  ## Specification revisions  | Rev. | Author | Date | Comments | | -- | -- | -- | -- | | 1 | C.J.Sendall | 12-Feb-07 | Created | | 2 | C.J.Sendall | 9-Aug-07 | Specify integer format of Mifare Number | | 3 | C.J.Sendall | 12-Jun-15 | Description of UL barcode changed | | 4 | E. Kirk (ek599) | 11-Sep-24 | Refine and consolidate card specification and other documentation. Moved and change format to markdown. |   ### Links to previous revisions  | Rev. | Link | | -- | -- | | 3 | https://docs.google.com/document/d/1WjfD5Ags-mBInKouvnledlShzjvYkq4RQuK7P5hoHPY |   ## Card technology  The University Card Office started using **Mifare classic 4K** cards for the University Card in August 2006. \"Mifare Classic\" defines both hardware requirements and the proprietary protocols used. Further details are available at https://www.mifare.net/ but generally card readers need to be specified to (completely) support \"Mifare Classic\", including the Mifare Classic 4K variant.  ## Read and write keys  In order to read from most fields on the card respective \"read keys\" are needed. If you need access to the read keys (e.g. when installing a new card readers), please contact universitycard-dev@uis.cam.ac.uk and they will be made available via a secure mechanism. The read keys need to be treated like passwords; they must be stored and managed securely and should never be shared with third parties.  Corresponding write keys are needed to write to blocks. These are not generally available outside of the card printing processes.  ## Security  Mifare Classic protocols have known exploits and are no longer considered secure. While the technology is in use, the UIS card team follows sensible security practices (e.g. keeping read keys secured).  ## Card Layout  ### Fields to use  The following fields can be used for the purpose of identifying cards and users for access control purposes. **No other fields are supported for access control purposes.**  | Fields | Location | | -- | -- | | UCam Card ID (historically, mifare number) | Sector 1 Block 2 |  ### Personal and access only cards  The following table indicates which fields are available on the 2 types of cards printed, \"Personal\" and \"Temporary Access Cards\".  | Fields | Personal | Temporary Access Cards | | -- | -- | -- | | (Globaly unique factory) MIFARE ID | x | x | | [DEPRECIATED] Cardholder ID* | x | | | [DEPRECIATED] Issue Number* | x | | | **UCam Card ID** (historically, Mifare Number)* | x | x | | [DEPRECIATED] CRSID | x | | | [DEPRECIATED] USN | x | | | [DEPRECIATED] Staff number | x | | | [DEPRECIATED] Expiry date | x | | | [DEPRECIATED] Issue date | x | | | [DEPRECIATED] UL barcode | x | |  *Fields marked as depreciated should no longer be accessed from the card itself.*  \\* See Endnotes - Card Reader Programming  ### Detailed card format  The card layout table lists all values that are **potentially** present on cards (see Personal and access only cards).  | Sector | Block 0 | Block 1 | Block 2 | Requires Read Keys | MAD | | -- | -- | -- | -- | -- | -- | | 0 | (Globaly unique factory) MIFARE ID | MAD directory | MAD directory | No | - | | 1 | [DEPRECIATED] Cardholder ID | [DEPRECIATED] Issue Number | **UCam Card ID** (historically, Mifare Number) | Yes | 5810 | | 2 | [DEPRECIATED] CRSID | [DEPRECIATED] USN | [DEPRECIATED] Staff number | Yes | 5811 | | 3 | [DEPRECIATED] Expiry date | [DEPRECIATED] Issue date | [DEPRECIATED] UL barcode | Yes | 5812 | | 4 | [DEPRECIATED] Cardholder ID* | [DEPRECIATED] Issue Number* | [LOCATION DEPRECIATED] UCam Card ID | Yes | 5813 | | 5-15 | | | | Yes | 0000 | | 16 | MAD2 directory | | MAD2 directory | No | - | | 17-33 | | | | Yes | 0000 | | 34-39 | | | | Yes | 0002 |   Fields marked as depreciated should no longer be accessed from the card itself. Some fields are available from Card API using the UCam Card ID to query data on users, e.g. to get CRSID.  MIFARE Application Directory (MAD) entries of 5810,5811,5812,5813 are Application Identifiers (AIDs). A MAD entry of  0002 means reserved and 0000 means free.  ### Data Specification  All sectors padded with trailing nulls or blanks  | Name | Charset | Length | Description | | -- | -- | -- | -- | | [DEPRECIATED] Cardholder ID | ASCII | 7 characters | two lower case letters, four digits , lower case  letter (checksum) | | [DEPRECIATED] Issue Number | ASCII | 2 digits | | | **UCam Card ID** (historically, Mifare Number) | integer | 32bits | Up to 8 digit integer (little-endian,  i.e. the least significant byte comes first) | | [DEPRECIATED] CRSID | ASCII | 4-7 characters | Upper case letters and digits | | [DEPRECIATED] USN | ASCII | 9 digits | | | [DEPRECIATED] Staff number | Up to 6 digits | | | [DEPRECIATED] Expiry date | ASCII | 10 | yyyy/mm/dd | | [DEPRECIATED] Issue date | ASCII | 10 | yyyy/mm/dd | | [DEPRECIATED] UL barcode | ASCII | 5 characters | 5 upper case letters and digits, starting with V |  ## Endnotes  ### Card Reader Programming It has been witnessed that some card readers have likely been programmed to calculate the UCam Card ID from the depreciated Cardholder ID and Issue Number. When personal cards are printed, they currently generate the UCam Card ID from the depreciated fields Cardholder ID and Issue Number using a legacy algorithm. Affected readers appear to use the same algorithm to generate or validate the UCam Card ID from these depreciated fields. It is unknown by the current team operating the card system why some readers were programmed in such a way. Temporary access cards printed since 2021 do not have the depreciated fields Cardholder ID and Issue Number and generate the UCam Card ID value differently. *Card readers that are not just using the UCam Card ID should be reprogrammed or replaced.*    # Card API  ## Introduction  The Card API allows access to information about University Cards.  The API broadly follows the principles of REST and strives to provide an interface that can be easily consumed by downstream systems.  ### Stability  This release of the Card API is a `beta` offering: a service we are moving towards live but which requires wider testing with a broader group of users. We consider the Card API as being at least as stable as the legacy card system which it aims to replace, so we encourage users to make use of the Card API rather than relying on the legacy card system.  ### Versioning  The Card API is versioned using url path prefixes in the format: `/v1beta1/cards`. This follows the pattern established by the [GCP API](https://cloud.google.com/apis/design/versioning). Breaking changes will not be made without a change in API major version, however non-breaking changes will be introduced without changes to the version path prefix. All changes will be documented in the project's [CHANGELOG](https://gitlab.developers.cam.ac.uk/uis/devops/iam/card-database/card-api/-/blob/master/CHANGELOG.md).  The available versions of the API are listed at the API's root.  ### Domain  The Card API has been designed to only expose information about University Cards and the identifiers which link a Card to a person. The API does not expose information about cardholders or the institutions that a cardholder belongs to. This is in order to combat domain crossover and to ensure the Card API does not duplicate information which is held and managed within systems such as Lookup, CamSIS or CHRIS.  It is expected that the Card API should be used alongside APIs such as Lookup which allow personal and institutional membership information to be retrieved. A tool has been written in order to allow efficient querying of the Card API using information contained within, CamSIS or CHRIS. [Usage and installation instructions for this tool can be found here](https://gitlab.developers.cam.ac.uk/uis/devops/iam/card-database/card-client).  ### Data source  The data exposed in the Card API is currently a mirror of data contained within the [Card Database](https://webservices.admin.cam.ac.uk/uc/). With data being synced from the Card Database to the Card API hourly.  In future, card data will be updated and created directly using the Card API so changes will be reflected in the Card API 'live' without this hourly sync.  ## Core entities  ### The `Card` Entity  The `Card` entity is a representation of a physical University Card. The entity contains fields indicating the status of the card and when the card has moved between different statuses. Cards held by individuals (such as students or staff) and temporary cards managed by institutions are both represented by the `Card` entity, with the former having a `cardType` of `MIFARE_PERSONAL` and the latter having a `cardType` of `MIFARE_TEMPORARY`.  Each card should have a set of `CardIdentifiers` which allow the card to be linked to an entity in another system (e.g. a person in Lookup), or record information about identifiers held within the card, such as Mifare ID.  The full `Card` entity contains a `cardNotes` field which holds a set of notes made by administrator users related to the card, as well as an `attributes` field which holds the data that is present on the physical presentation of a card. Operations which list many cards return `CardSummary` entities which omit these fields for brevity.  ### The `CardIdentifier` Entity  The `CardIdentifier` entity holds the `value` and `scheme` of a given identifier. The `value` field of a `CardIdentifier` is a simple ID string - e.g. `wgd23` or `000001`. The `scheme` field of a `CardIdentifier` indicates what system this identifier relates to or was issued by. This allows many identifiers which relate to different systems to be recorded against a single `Card`.  > **WARNING!** > > A barcode identifier (`barcode.v1.card.university.identifiers.cam.ac.uk`) may be associated with more than one user. See `Known Issues` for more details.  The supported schemes are: * `v1.person.identifiers.cam.ac.uk`: The CRSid of the person who holds this card * `person.v1.student-records.university.identifiers.cam.ac.uk`: The CamSIS identifier (USN) of the person who holds this card * `person.v1.human-resources.university.identifiers.cam.ac.uk`: The CHRIS identifier (staff number) of the person who holds this card * `person.v1.board-of-graduate-studies.university.identifiers.cam.ac.uk`: The Board of Graduate Studies identifier of the person who holds this card * `person.v1.legacy-card.university.identifiers.cam.ac.uk`: The legacy card holder ID for the person who holds this card * `mifare-identifier.v1.card.university.identifiers.cam.ac.uk`: The Mifare ID which is embedded in this card (this     identifier uniquely identifies a single card) * `mifare-number.v1.card.university.identifiers.cam.ac.uk`: The Mifare Number which is embedded in this card     (this identifier is a digest of card's legacy cardholder ID and issue number, so is not     guaranteed to be unique) * `card.v1.legacy-card.university.identifiers.cam.ac.uk`: The legacy card ID from the card database * `temporary-card.v1.card.university.identifiers.cam.ac.uk`: The temporary card ID from the card database * `photo.v1.photo.university.identifiers.cam.ac.uk`: The ID of the photo printed on this card * `barcode.v1.card.university.identifiers.cam.ac.uk`: The barcode printed on this card * `institution.v1.legacy-card.university.identifiers.cam.ac.uk`: The legacy institution ID from the card database (only populated on temporary cards)   ## Using the API  ### Auth  To authenticate against the Card API, an application must be registered within the API Service, the application must be owned by a team account as opposed to an individual account and the application must be granted access to the `University Card` product. Details of how to register an application and grant access to products can be found in the [API Service Getting Started Guide](https://developer.api.apps.cam.ac.uk/start-using-an-api).  #### Principal  Throughout this specification the term `principal` is used to describe the user or service who is making use of the API. When authenticating using the OAuth2 client credentials flow the principal shall be the application registered within the API Gateway. When authenticating using the authorization code flow, e.g. via a Single Page Application, the principal shall be the user who has authenticated and consented to give the application access to the data contained within this API - identified by their CRSid.  This specification references permissions which can be granted to any principal - please contact the API maintainers to grant a principal a specific permission.  ### Content Type  The Card API responds with JSON data. The `Content-Type` request header should be omitted or set to `application/json`. If an invalid `Content-Type` header is sent the API will respond with `415 Unsupported Media Type`.  ### Pagination  For all operations where multiple entities will be returned, the API will return a paginated result. This is to account for too many entities needing to be returned within a single response. A Paginated response has the structure:  ```json {   \"next\": \"https://<gateway_host>/card/v1beta1/cards/?cursor=cD0yMDIxLTAxL   \"previous\": null,   \"results\": [       ... the data for the current page   ] }  ```  The `next` field holds the url of the next page of results, containing a cursor which indicates to the API which page of results to return. If the `next` field is `null` no further results are available. The `previous` field can be used to navigate backwards through pages of results.  The `page_size` query parameter can be used to control the number of results to return. This defaults to 200 but can be set to a maximum of 500, if set to greater than this no error will be returned but only 500 results will be given in the response.  ## Known Issues  ### Barcodes  There are barcodes in the Card API that are associated with multiple users. The two main causes of this are:   - imported records from the previous card system   - a bug that existed in the current system were the same barcode is assigned to multiple users     created at the same time  The Card API service team are working towards no active cards (status=ISSUED) sharing the same barcode. Defences have been put it place to prevent new duplicate barcodes occurring.  **Clients of the Card API should expect expired cards and card requests to potentially be associated with a barcode that is also associated with cards and card requests of a different user. As the `card-identifiers` endpoint uses all cards/card requests to link identifiers, when looking up using effected barcodes, multiple users (via identifiers) will always remain associated.**  The `discontinued-identifiers` endpoint provides details of identifiers that are no longer to be **reused**. Records in `discontinued-identifiers` prevent reusing the specified identifier with **new** card requests. This endpoint can be queried for barcodes that have been identified as being associated with multiple users.  

    The version of the OpenAPI document: v1beta1
    Contact: universitycard-dev@uis.cam.ac.uk
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, StrictStr
from typing import Any, ClassVar, Dict, List
from typing import Optional, Set
from typing_extensions import Self

class CollegeInstituionsIdsListResponseType(BaseModel):
    """
    CollegeInstituionsIdsListResponseType
    """ # noqa: E501
    results: List[StrictStr]
    __properties: ClassVar[List[str]] = ["results"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of CollegeInstituionsIdsListResponseType from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of CollegeInstituionsIdsListResponseType from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "results": obj.get("results")
        })
        return _obj


