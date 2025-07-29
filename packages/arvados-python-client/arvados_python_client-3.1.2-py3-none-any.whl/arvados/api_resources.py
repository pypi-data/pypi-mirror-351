"""Arvados API client reference documentation

This module provides reference documentation for the interface of the
Arvados API client, including method signatures and type information for
returned objects. However, the functions in `arvados.api` will return
different classes at runtime that are generated dynamically from the Arvados
API discovery document. The classes in this module do not have any
implementation, and you should not instantiate them in your code.

If you're just starting out, `ArvadosAPIClient` documents the methods
available from the client object. From there, you can follow the trail into
resource methods, request objects, and finally the data dictionaries returned
by the API server.
"""

import googleapiclient.discovery
import googleapiclient.http
import httplib2
import sys
from typing import Any, Dict, Generic, List, Literal, Optional, TypedDict, TypeVar

# ST represents an API response type
ST = TypeVar('ST', bound=TypedDict)


class ArvadosAPIRequest(googleapiclient.http.HttpRequest, Generic[ST]):
    """Generic API request object

    When you call an API method in the Arvados Python SDK, it returns a
    request object. You usually call `execute()` on this object to submit the
    request to your Arvados API server and retrieve the response. `execute()`
    will return the type of object annotated in the subscript of
    `ArvadosAPIRequest`.
    """

    def execute(self, http: Optional[httplib2.Http]=None, num_retries: int=0) -> ST:
        """Execute this request and return the response

        Arguments:

        * http: httplib2.Http | None --- The HTTP client object to use to
          execute the request. If not specified, uses the HTTP client object
          created with the API client object.

        * num_retries: int --- The maximum number of times to retry this
          request if the server returns a retryable failure. The API client
          object also has a maximum number of retries specified when it is
          instantiated (see `arvados.api.api_client`). This request is run
          with the larger of that number and this argument. Default 0.
        """


class ApiClientAuthorization(TypedDict, total=False):
    """Arvados API client authorization token

    This resource represents an API token a user may use to authenticate an
    Arvados API request.

    This is the dictionary object that represents a single ApiClientAuthorization in Arvados
    and is returned by most `ApiClientAuthorizations` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    etag: 'str'
    """Object cache version."""
    api_token: 'str'
    """The secret token that can be used to authorize Arvados API requests."""
    created_by_ip_address: 'str'
    """The IP address of the client that created this token."""
    last_used_by_ip_address: 'str'
    """The IP address of the client that last used this token."""
    last_used_at: 'str'
    """The last time this token was used to authorize a request. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    expires_at: 'str'
    """The time after which this token is no longer valid for authorization. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    created_at: 'str'
    """The time this API client authorization was created. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    scopes: 'List'
    """An array of strings identifying HTTP methods and API paths this token is
    authorized to use. Refer to the [scopes reference][] for details.

    [scopes reference]: https://doc.arvados.org/api/tokens.html#scopes
    """
    uuid: 'str'
    """This API client authorization's Arvados UUID, like `zzzzz-gj3su-12345abcde67890`."""


class ApiClientAuthorizationList(TypedDict, total=False):
    """A list of ApiClientAuthorization objects.

    This is the dictionary object returned when you call `ApiClientAuthorizations.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `ApiClientAuthorization` objects.
    """
    kind: 'str' = 'arvados#apiClientAuthorizationList'
    """Object type. Always arvados#apiClientAuthorizationList."""
    etag: 'str'
    """List cache version."""
    items: 'List[ApiClientAuthorization]'
    """An array of matching ApiClientAuthorization objects."""


class ApiClientAuthorizations:
    """Methods to query and manipulate Arvados api client authorizations"""

    def create(self, *, body: "Dict[Literal['api_client_authorization'], ApiClientAuthorization]", cluster_id: 'Optional[str]' = None, ensure_unique_name: 'bool' = False, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[ApiClientAuthorization]':
        """Create a new ApiClientAuthorization.

        Required parameters:

        * body: Dict[Literal['api_client_authorization'], ApiClientAuthorization] --- A dictionary with a single item `'api_client_authorization'`.
          Its value is a `ApiClientAuthorization` dictionary defining the attributes to set. 

        Optional parameters:

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster where this object should be created. 

        * ensure_unique_name: bool --- If the given name is already used by this owner, adjust the name to ensure uniqueness instead of returning an error. Default `False`.

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def create_system_auth(self, *, scopes: 'List' = ['all']) -> 'ArvadosAPIRequest[ApiClientAuthorization]':
        """Create a token for the system ("root") user.

        Optional parameters:

        * scopes: List --- An array of strings defining the scope of resources this token will be allowed to access. Refer to the [scopes reference][] for details. Default `['all']`.

          [scopes reference]: https://doc.arvados.org/api/tokens.html#scopes
        """

    def current(self) -> 'ArvadosAPIRequest[ApiClientAuthorization]':
        """Return all metadata for the token used to authorize this request."""

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[ApiClientAuthorization]':
        """Delete an existing ApiClientAuthorization.

        Required parameters:

        * uuid: str --- The UUID of the ApiClientAuthorization to delete.
        """

    def get(self, *, uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[ApiClientAuthorization]':
        """Get a ApiClientAuthorization record by UUID.

        Required parameters:

        * uuid: str --- The UUID of the ApiClientAuthorization to return. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def list(self, *, bypass_federation: 'bool' = False, cluster_id: 'Optional[str]' = None, count: 'str' = 'exact', distinct: 'bool' = False, filters: 'Optional[List]' = None, limit: 'int' = 100, offset: 'int' = 0, order: 'Optional[List]' = None, select: 'Optional[List]' = None, where: 'Optional[Dict[str, Any]]' = None) -> 'ArvadosAPIRequest[ApiClientAuthorizationList]':
        """Retrieve a ApiClientAuthorizationList.

        This method returns a single page of `ApiClientAuthorization` objects that match your search
        criteria. If you just want to iterate all objects that match your search
        criteria, consider using `arvados.util.keyset_list_all`.

        Optional parameters:

        * bypass_federation: bool --- If true, do not return results from other clusters in the
          federation, only the cluster that received the request.
          You must be an administrator to use this flag. Default `False`.

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster to return objects from 

        * count: str --- A string to determine result counting behavior. Supported values are:

          * `"exact"`: The response will include an `items_available` field that
            counts the number of objects that matched this search criteria,
            including ones not included in `items`.

          * `"none"`: The response will not include an `items_avaliable`
            field. This improves performance by returning a result as soon as enough
            `items` have been loaded for this result.

          Default `'exact'`.

        * distinct: bool --- If this is true, and multiple objects have the same values
          for the attributes that you specify in the `select` parameter, then each unique
          set of values will only be returned once in the result set. Default `False`.

        * filters: Optional[List] --- Filters to limit which objects are returned by their attributes.
          Refer to the [filters reference][] for more information about how to write filters. 

          [filters reference]: https://doc.arvados.org/api/methods.html#filters

        * limit: int --- The maximum number of objects to return in the result.
          Note that the API may return fewer results than this if your request hits other
          limits set by the administrator. Default `100`.

        * offset: int --- Return matching objects starting from this index.
          Note that result indexes may change if objects are modified in between a series
          of list calls. Default `0`.

        * order: Optional[List] --- An array of strings to set the order in which matching objects are returned.
          Each string has the format `<ATTRIBUTE> <DIRECTION>`.
          `DIRECTION` can be `asc` or omitted for ascending, or `desc` for descending. 

        * select: Optional[List] --- An array of names of attributes to return from each matching object. 

        * where: Optional[Dict[str, Any]] --- An object to limit which objects are returned by their attributes.
          The keys of this object are attribute names.
          Each value is either a single matching value or an array of matching values for that attribute.
          The `filters` parameter is more flexible and preferred.
        """

    def update(self, *, body: "Dict[Literal['api_client_authorization'], ApiClientAuthorization]", uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[ApiClientAuthorization]':
        """Update attributes of an existing ApiClientAuthorization.

        Required parameters:

        * body: Dict[Literal['api_client_authorization'], ApiClientAuthorization] --- A dictionary with a single item `'api_client_authorization'`.
          Its value is a `ApiClientAuthorization` dictionary defining the attributes to set. 

        * uuid: str --- The UUID of the ApiClientAuthorization to update. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """


class AuthorizedKey(TypedDict, total=False):
    """Arvados authorized public key

    This resource represents a public key a user may use to authenticate themselves
    to services on the cluster. Its primary use today is to store SSH keys for
    virtual machines ("shell nodes"). It may be extended to store other keys in
    the future.

    This is the dictionary object that represents a single AuthorizedKey in Arvados
    and is returned by most `AuthorizedKeys` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    etag: 'str'
    """Object cache version."""
    uuid: 'str'
    """This authorized key's Arvados UUID, like `zzzzz-fngyi-12345abcde67890`."""
    owner_uuid: 'str'
    """The UUID of the user or group that owns this authorized key."""
    modified_by_user_uuid: 'str'
    """The UUID of the user that last updated this authorized key."""
    modified_at: 'str'
    """The time this authorized key was last updated. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    name: 'str'
    """The name of this authorized key assigned by a user."""
    key_type: 'str'
    """A string identifying what type of service uses this key. Supported values are:

      * `"SSH"`
    """
    authorized_user_uuid: 'str'
    """The UUID of the Arvados user that is authorized by this key."""
    public_key: 'str'
    """The full public key, in the format referenced by `key_type`."""
    expires_at: 'str'
    """The time after which this key is no longer valid for authorization. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    created_at: 'str'
    """The time this authorized key was created. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""


class AuthorizedKeyList(TypedDict, total=False):
    """A list of AuthorizedKey objects.

    This is the dictionary object returned when you call `AuthorizedKeys.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `AuthorizedKey` objects.
    """
    kind: 'str' = 'arvados#authorizedKeyList'
    """Object type. Always arvados#authorizedKeyList."""
    etag: 'str'
    """List cache version."""
    items: 'List[AuthorizedKey]'
    """An array of matching AuthorizedKey objects."""


class AuthorizedKeys:
    """Methods to query and manipulate Arvados authorized keys"""

    def create(self, *, body: "Dict[Literal['authorized_key'], AuthorizedKey]", cluster_id: 'Optional[str]' = None, ensure_unique_name: 'bool' = False, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[AuthorizedKey]':
        """Create a new AuthorizedKey.

        Required parameters:

        * body: Dict[Literal['authorized_key'], AuthorizedKey] --- A dictionary with a single item `'authorized_key'`.
          Its value is a `AuthorizedKey` dictionary defining the attributes to set. 

        Optional parameters:

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster where this object should be created. 

        * ensure_unique_name: bool --- If the given name is already used by this owner, adjust the name to ensure uniqueness instead of returning an error. Default `False`.

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[AuthorizedKey]':
        """Delete an existing AuthorizedKey.

        Required parameters:

        * uuid: str --- The UUID of the AuthorizedKey to delete.
        """

    def get(self, *, uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[AuthorizedKey]':
        """Get a AuthorizedKey record by UUID.

        Required parameters:

        * uuid: str --- The UUID of the AuthorizedKey to return. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def list(self, *, bypass_federation: 'bool' = False, cluster_id: 'Optional[str]' = None, count: 'str' = 'exact', distinct: 'bool' = False, filters: 'Optional[List]' = None, limit: 'int' = 100, offset: 'int' = 0, order: 'Optional[List]' = None, select: 'Optional[List]' = None, where: 'Optional[Dict[str, Any]]' = None) -> 'ArvadosAPIRequest[AuthorizedKeyList]':
        """Retrieve a AuthorizedKeyList.

        This method returns a single page of `AuthorizedKey` objects that match your search
        criteria. If you just want to iterate all objects that match your search
        criteria, consider using `arvados.util.keyset_list_all`.

        Optional parameters:

        * bypass_federation: bool --- If true, do not return results from other clusters in the
          federation, only the cluster that received the request.
          You must be an administrator to use this flag. Default `False`.

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster to return objects from 

        * count: str --- A string to determine result counting behavior. Supported values are:

          * `"exact"`: The response will include an `items_available` field that
            counts the number of objects that matched this search criteria,
            including ones not included in `items`.

          * `"none"`: The response will not include an `items_avaliable`
            field. This improves performance by returning a result as soon as enough
            `items` have been loaded for this result.

          Default `'exact'`.

        * distinct: bool --- If this is true, and multiple objects have the same values
          for the attributes that you specify in the `select` parameter, then each unique
          set of values will only be returned once in the result set. Default `False`.

        * filters: Optional[List] --- Filters to limit which objects are returned by their attributes.
          Refer to the [filters reference][] for more information about how to write filters. 

          [filters reference]: https://doc.arvados.org/api/methods.html#filters

        * limit: int --- The maximum number of objects to return in the result.
          Note that the API may return fewer results than this if your request hits other
          limits set by the administrator. Default `100`.

        * offset: int --- Return matching objects starting from this index.
          Note that result indexes may change if objects are modified in between a series
          of list calls. Default `0`.

        * order: Optional[List] --- An array of strings to set the order in which matching objects are returned.
          Each string has the format `<ATTRIBUTE> <DIRECTION>`.
          `DIRECTION` can be `asc` or omitted for ascending, or `desc` for descending. 

        * select: Optional[List] --- An array of names of attributes to return from each matching object. 

        * where: Optional[Dict[str, Any]] --- An object to limit which objects are returned by their attributes.
          The keys of this object are attribute names.
          Each value is either a single matching value or an array of matching values for that attribute.
          The `filters` parameter is more flexible and preferred.
        """

    def update(self, *, body: "Dict[Literal['authorized_key'], AuthorizedKey]", uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[AuthorizedKey]':
        """Update attributes of an existing AuthorizedKey.

        Required parameters:

        * body: Dict[Literal['authorized_key'], AuthorizedKey] --- A dictionary with a single item `'authorized_key'`.
          Its value is a `AuthorizedKey` dictionary defining the attributes to set. 

        * uuid: str --- The UUID of the AuthorizedKey to update. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """


class Collection(TypedDict, total=False):
    """Arvados data collection

    A collection describes how a set of files is stored in data blocks in Keep,
    along with associated metadata.

    This is the dictionary object that represents a single Collection in Arvados
    and is returned by most `Collections` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    etag: 'str'
    """Object cache version."""
    owner_uuid: 'str'
    """The UUID of the user or group that owns this collection."""
    created_at: 'str'
    """The time this collection was created. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_user_uuid: 'str'
    """The UUID of the user that last updated this collection."""
    modified_at: 'str'
    """The time this collection was last updated. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    portable_data_hash: 'str'
    """The portable data hash of this collection. This string provides a unique
    and stable reference to these contents.
    """
    replication_desired: 'int'
    """The number of copies that should be made for data in this collection."""
    replication_confirmed_at: 'str'
    """The last time the cluster confirmed that it met `replication_confirmed`
    for this collection. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`.
    """
    replication_confirmed: 'int'
    """The number of copies of data in this collection that the cluster has confirmed
    exist in storage.
    """
    uuid: 'str'
    """This collection's Arvados UUID, like `zzzzz-4zz18-12345abcde67890`."""
    manifest_text: 'str'
    """The manifest text that describes how files are constructed from data blocks
    in this collection. Refer to the [manifest format][] reference for details.

    [manifest format]: https://doc.arvados.org/architecture/manifest-format.html
    """
    name: 'str'
    """The name of this collection assigned by a user."""
    description: 'str'
    """A longer HTML description of this collection assigned by a user.
    Allowed HTML tags are `a`, `b`, `blockquote`, `br`, `code`,
    `del`, `dd`, `dl`, `dt`, `em`, `h1`, `h2`, `h3`, `h4`, `h5`, `h6`, `hr`,
    `i`, `img`, `kbd`, `li`, `ol`, `p`, `pre`,
    `s`, `section`, `span`, `strong`, `sub`, `sup`, and `ul`.
    """
    properties: 'Dict[str, Any]'
    """A hash of arbitrary metadata for this collection.
    Some keys may be reserved by Arvados or defined by a configured vocabulary.
    Refer to the [metadata properties reference][] for details.

    [metadata properties reference]: https://doc.arvados.org/api/properties.html
    """
    delete_at: 'str'
    """The time this collection will be permanently deleted. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    trash_at: 'str'
    """The time this collection will be trashed. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    is_trashed: 'bool'
    """A boolean flag to indicate whether or not this collection is trashed."""
    storage_classes_desired: 'List'
    """An array of strings identifying the storage class(es) that should be used
    for data in this collection. Storage classes are configured by the cluster administrator.
    """
    storage_classes_confirmed: 'List'
    """An array of strings identifying the storage class(es) the cluster has
    confirmed have a copy of this collection's data.
    """
    storage_classes_confirmed_at: 'str'
    """The last time the cluster confirmed that data was stored on the storage
    class(es) in `storage_classes_confirmed`. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`.
    """
    current_version_uuid: 'str'
    """The UUID of the current version of this collection."""
    version: 'int'
    """An integer that counts which version of a collection this record
    represents. Refer to [collection versioning][] for details. This attribute is
    read-only.

    [collection versioning]: https://doc.arvados.org/user/topics/collection-versioning.html
    """
    preserve_version: 'bool'
    """A boolean flag to indicate whether this specific version of this collection
    should be persisted in cluster storage.
    """
    file_count: 'int'
    """The number of files represented in this collection's `manifest_text`.
    This attribute is read-only.
    """
    file_size_total: 'int'
    """The total size in bytes of files represented in this collection's `manifest_text`.
    This attribute is read-only.
    """


class CollectionList(TypedDict, total=False):
    """A list of Collection objects.

    This is the dictionary object returned when you call `Collections.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `Collection` objects.
    """
    kind: 'str' = 'arvados#collectionList'
    """Object type. Always arvados#collectionList."""
    etag: 'str'
    """List cache version."""
    items: 'List[Collection]'
    """An array of matching Collection objects."""


class Collections:
    """Methods to query and manipulate Arvados collections"""

    def create(self, *, body: "Dict[Literal['collection'], Collection]", cluster_id: 'Optional[str]' = None, ensure_unique_name: 'bool' = False, replace_files: 'Optional[Dict[str, Any]]' = None, replace_segments: 'Optional[Dict[str, Any]]' = None, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[Collection]':
        """Create a new Collection.

        Required parameters:

        * body: Dict[Literal['collection'], Collection] --- A dictionary with a single item `'collection'`.
          Its value is a `Collection` dictionary defining the attributes to set. 

        Optional parameters:

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster where this object should be created. 

        * ensure_unique_name: bool --- If the given name is already used by this owner, adjust the name to ensure uniqueness instead of returning an error. Default `False`.

        * replace_files: Optional[Dict[str, Any]] --- Add, delete, and replace files and directories with new content
          and/or content from other collections. Refer to the
          [replace_files reference][] for details. 

          [replace_files reference]: https://doc.arvados.org/api/methods/collections.html#replace_files

        * replace_segments: Optional[Dict[str, Any]] --- Replace existing block segments in the collection with new segments.
          Refer to the [replace_segments reference][] for details. 

          [replace_segments reference]: https://doc.arvados.org/api/methods/collections.html#replace_segments

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Collection]':
        """Delete an existing Collection.

        Required parameters:

        * uuid: str --- The UUID of the Collection to delete.
        """

    def get(self, *, uuid: 'str', include_trash: 'bool' = False, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[Collection]':
        """Get a Collection record by UUID.

        Required parameters:

        * uuid: str --- The UUID of the Collection to return. 

        Optional parameters:

        * include_trash: bool --- Show collection even if its `is_trashed` attribute is true. Default `False`.

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def list(self, *, bypass_federation: 'bool' = False, cluster_id: 'Optional[str]' = None, count: 'str' = 'exact', distinct: 'bool' = False, filters: 'Optional[List]' = None, include_old_versions: 'bool' = False, include_trash: 'bool' = False, limit: 'int' = 100, offset: 'int' = 0, order: 'Optional[List]' = None, select: 'Optional[List]' = None, where: 'Optional[Dict[str, Any]]' = None) -> 'ArvadosAPIRequest[CollectionList]':
        """Retrieve a CollectionList.

        This method returns a single page of `Collection` objects that match your search
        criteria. If you just want to iterate all objects that match your search
        criteria, consider using `arvados.util.keyset_list_all`.

        Optional parameters:

        * bypass_federation: bool --- If true, do not return results from other clusters in the
          federation, only the cluster that received the request.
          You must be an administrator to use this flag. Default `False`.

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster to return objects from 

        * count: str --- A string to determine result counting behavior. Supported values are:

          * `"exact"`: The response will include an `items_available` field that
            counts the number of objects that matched this search criteria,
            including ones not included in `items`.

          * `"none"`: The response will not include an `items_avaliable`
            field. This improves performance by returning a result as soon as enough
            `items` have been loaded for this result.

          Default `'exact'`.

        * distinct: bool --- If this is true, and multiple objects have the same values
          for the attributes that you specify in the `select` parameter, then each unique
          set of values will only be returned once in the result set. Default `False`.

        * filters: Optional[List] --- Filters to limit which objects are returned by their attributes.
          Refer to the [filters reference][] for more information about how to write filters. 

          [filters reference]: https://doc.arvados.org/api/methods.html#filters

        * include_old_versions: bool --- Include past collection versions. Default `False`.

        * include_trash: bool --- Include collections whose `is_trashed` attribute is true. Default `False`.

        * limit: int --- The maximum number of objects to return in the result.
          Note that the API may return fewer results than this if your request hits other
          limits set by the administrator. Default `100`.

        * offset: int --- Return matching objects starting from this index.
          Note that result indexes may change if objects are modified in between a series
          of list calls. Default `0`.

        * order: Optional[List] --- An array of strings to set the order in which matching objects are returned.
          Each string has the format `<ATTRIBUTE> <DIRECTION>`.
          `DIRECTION` can be `asc` or omitted for ascending, or `desc` for descending. 

        * select: Optional[List] --- An array of names of attributes to return from each matching object. 

        * where: Optional[Dict[str, Any]] --- An object to limit which objects are returned by their attributes.
          The keys of this object are attribute names.
          Each value is either a single matching value or an array of matching values for that attribute.
          The `filters` parameter is more flexible and preferred.
        """

    def provenance(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Collection]':
        """Detail the provenance of a given collection.

        Required parameters:

        * uuid: str --- The UUID of the Collection to query.
        """

    def trash(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Collection]':
        """Trash a collection.

        Required parameters:

        * uuid: str --- The UUID of the Collection to update.
        """

    def untrash(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Collection]':
        """Untrash a collection.

        Required parameters:

        * uuid: str --- The UUID of the Collection to update.
        """

    def update(self, *, body: "Dict[Literal['collection'], Collection]", uuid: 'str', replace_files: 'Optional[Dict[str, Any]]' = None, replace_segments: 'Optional[Dict[str, Any]]' = None, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[Collection]':
        """Update attributes of an existing Collection.

        Required parameters:

        * body: Dict[Literal['collection'], Collection] --- A dictionary with a single item `'collection'`.
          Its value is a `Collection` dictionary defining the attributes to set. 

        * uuid: str --- The UUID of the Collection to update. 

        Optional parameters:

        * replace_files: Optional[Dict[str, Any]] --- Add, delete, and replace files and directories with new content
          and/or content from other collections. Refer to the
          [replace_files reference][] for details. 

          [replace_files reference]: https://doc.arvados.org/api/methods/collections.html#replace_files

        * replace_segments: Optional[Dict[str, Any]] --- Replace existing block segments in the collection with new segments.
          Refer to the [replace_segments reference][] for details. 

          [replace_segments reference]: https://doc.arvados.org/api/methods/collections.html#replace_segments

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def used_by(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Collection]':
        """Detail where a given collection has been used.

        Required parameters:

        * uuid: str --- The UUID of the Collection to query.
        """


class ComputedPermission(TypedDict, total=False):
    """Arvados computed permission

    Computed permissions do not correspond directly to any Arvados resource, but
    provide a simple way to query the entire graph of permissions granted to
    users and groups.

    This is the dictionary object that represents a single ComputedPermission in Arvados
    and is returned by most `ComputedPermissions` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    user_uuid: 'str'
    """The UUID of the Arvados user who has this permission."""
    target_uuid: 'str'
    """The UUID of the Arvados object the user has access to."""
    perm_level: 'str'
    """A string representing the user's level of access to the target object.
    Possible values are:

      * `"can_read"`
      * `"can_write"`
      * `"can_manage"`
    """


class ComputedPermissionList(TypedDict, total=False):
    """A list of ComputedPermission objects.

    This is the dictionary object returned when you call `ComputedPermissions.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.iter_computed_permissions`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `ComputedPermission` objects.
    """
    kind: 'str' = 'arvados#computedPermissionList'
    """Object type. Always arvados#computedPermissionList."""
    etag: 'str'
    """List cache version."""
    items: 'List[ComputedPermission]'
    """An array of matching ComputedPermission objects."""


class ComputedPermissions:
    """Methods to query and manipulate Arvados computed permissions"""

    def list(self, *, count: 'str' = 'exact', distinct: 'bool' = False, filters: 'Optional[List]' = None, limit: 'int' = 100, order: 'Optional[List]' = None, select: 'Optional[List]' = None, where: 'Optional[Dict[str, Any]]' = None) -> 'ArvadosAPIRequest[ComputedPermissionList]':
        """Retrieve a ComputedPermissionList.

        This method returns a single page of `ComputedPermission` objects that match your search
        criteria. If you just want to iterate all objects that match your search
        criteria, consider using `arvados.util.iter_computed_permissions`.

        Optional parameters:

        * count: str --- A string to determine result counting behavior. Supported values are:

          * `"exact"`: The response will include an `items_available` field that
            counts the number of objects that matched this search criteria,
            including ones not included in `items`.

          * `"none"`: The response will not include an `items_avaliable`
            field. This improves performance by returning a result as soon as enough
            `items` have been loaded for this result.

          Default `'exact'`.

        * distinct: bool --- If this is true, and multiple objects have the same values
          for the attributes that you specify in the `select` parameter, then each unique
          set of values will only be returned once in the result set. Default `False`.

        * filters: Optional[List] --- Filters to limit which objects are returned by their attributes.
          Refer to the [filters reference][] for more information about how to write filters. 

          [filters reference]: https://doc.arvados.org/api/methods.html#filters

        * limit: int --- The maximum number of objects to return in the result.
          Note that the API may return fewer results than this if your request hits other
          limits set by the administrator. Default `100`.

        * order: Optional[List] --- An array of strings to set the order in which matching objects are returned.
          Each string has the format `<ATTRIBUTE> <DIRECTION>`.
          `DIRECTION` can be `asc` or omitted for ascending, or `desc` for descending. 

        * select: Optional[List] --- An array of names of attributes to return from each matching object. 

        * where: Optional[Dict[str, Any]] --- An object to limit which objects are returned by their attributes.
          The keys of this object are attribute names.
          Each value is either a single matching value or an array of matching values for that attribute.
          The `filters` parameter is more flexible and preferred.
        """


class Configs:
    """Methods to query and manipulate Arvados configs"""

    def get(self) -> 'ArvadosAPIRequest[Dict[str, Any]]':
        """Get this cluster's public configuration settings."""


class ContainerRequest(TypedDict, total=False):
    """Arvados container request

    A container request represents a user's request that Arvados do some compute
    work, along with full details about what work should be done. Arvados will
    attempt to fulfill the request by mapping it to a matching container record,
    running the work on demand if necessary.

    This is the dictionary object that represents a single ContainerRequest in Arvados
    and is returned by most `ContainerRequests` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    etag: 'str'
    """Object cache version."""
    uuid: 'str'
    """This container request's Arvados UUID, like `zzzzz-xvhdp-12345abcde67890`."""
    owner_uuid: 'str'
    """The UUID of the user or group that owns this container request."""
    created_at: 'str'
    """The time this container request was created. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_at: 'str'
    """The time this container request was last updated. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_user_uuid: 'str'
    """The UUID of the user that last updated this container request."""
    name: 'str'
    """The name of this container request assigned by a user."""
    description: 'str'
    """A longer HTML description of this container request assigned by a user.
    Allowed HTML tags are `a`, `b`, `blockquote`, `br`, `code`,
    `del`, `dd`, `dl`, `dt`, `em`, `h1`, `h2`, `h3`, `h4`, `h5`, `h6`, `hr`,
    `i`, `img`, `kbd`, `li`, `ol`, `p`, `pre`,
    `s`, `section`, `span`, `strong`, `sub`, `sup`, and `ul`.
    """
    properties: 'Dict[str, Any]'
    """A hash of arbitrary metadata for this container request.
    Some keys may be reserved by Arvados or defined by a configured vocabulary.
    Refer to the [metadata properties reference][] for details.

    [metadata properties reference]: https://doc.arvados.org/api/properties.html
    """
    state: 'str'
    """A string indicating where this container request is in its lifecycle.
    Possible values are:

      * `"Uncommitted"` --- The container request has not been finalized and can still be edited.
      * `"Committed"` --- The container request is ready to be fulfilled.
      * `"Final"` --- The container request has been fulfilled or cancelled.
    """
    requesting_container_uuid: 'str'
    """The UUID of the container that created this container request, if any."""
    container_uuid: 'str'
    """The UUID of the container that fulfills this container request, if any."""
    container_count_max: 'int'
    """An integer that defines the maximum number of times Arvados should attempt
    to dispatch a container to fulfill this container request.
    """
    mounts: 'Dict[str, Any]'
    """A hash where each key names a directory inside this container, and its
    value is an object that defines the mount source for that directory. Refer
    to the [mount types reference][] for details.

    [mount types reference]: https://doc.arvados.org/api/methods/containers.html#mount_types
    """
    runtime_constraints: 'Dict[str, Any]'
    """A hash that identifies compute resources this container requires to run
    successfully. See the [runtime constraints reference][] for details.

    [runtime constraints reference]: https://doc.arvados.org/api/methods/containers.html#runtime_constraints
    """
    container_image: 'str'
    """The portable data hash of the Arvados collection that contains the image
    to use for this container.
    """
    environment: 'Dict[str, Any]'
    """A hash of string keys and values that defines the environment variables
    for the dispatcher to set when it executes this container.
    """
    cwd: 'str'
    """A string that the defines the working directory that the dispatcher should
    use when it executes the command inside this container.
    """
    command: 'List'
    """An array of strings that defines the command that the dispatcher should
    execute inside this container.
    """
    output_path: 'str'
    """A string that defines the file or directory path where the command
    writes output that should be saved from this container.
    """
    priority: 'int'
    """An integer between 0 and 1000 (inclusive) that represents this container request's
    scheduling priority. 0 represents a request to be cancelled. Higher
    values represent higher priority. Refer to the [priority reference][] for details.

    [priority reference]: https://doc.arvados.org/api/methods/container_requests.html#priority
    """
    expires_at: 'str'
    """The time after which this container request will no longer be fulfilled. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    filters: 'str'
    """Filters that limit which existing containers are eligible to satisfy this
    container request. This attribute is not implemented yet and should be null.
    """
    container_count: 'int'
    """An integer that records how many times Arvados has attempted to dispatch
    a container to fulfill this container request.
    """
    use_existing: 'bool'
    """A boolean flag. If set, Arvados may choose to satisfy this container
    request with an eligible container that already exists. Otherwise, Arvados will
    satisfy this container request with a newer container, which will usually result
    in the container running again.
    """
    scheduling_parameters: 'Dict[str, Any]'
    """A hash of scheduling parameters that should be passed to the underlying
    dispatcher when this container is run.
    See the [scheduling parameters reference][] for details.

    [scheduling parameters reference]: https://doc.arvados.org/api/methods/containers.html#scheduling_parameters
    """
    output_uuid: 'str'
    """The UUID of the Arvados collection that contains output for all the
    container(s) that were dispatched to fulfill this container request.
    """
    log_uuid: 'str'
    """The UUID of the Arvados collection that contains logs for all the
    container(s) that were dispatched to fulfill this container request.
    """
    output_name: 'str'
    """The name to set on the output collection of this container request."""
    output_ttl: 'int'
    """An integer in seconds. If greater than zero, when an output collection is
    created for this container request, its `expires_at` attribute will be set this
    far in the future.
    """
    output_storage_classes: 'List'
    """An array of strings identifying the storage class(es) that should be set
    on the output collection of this container request. Storage classes are configured by
    the cluster administrator.
    """
    output_properties: 'Dict[str, Any]'
    """A hash of arbitrary metadata to set on the output collection of this container request.
    Some keys may be reserved by Arvados or defined by a configured vocabulary.
    Refer to the [metadata properties reference][] for details.

    [metadata properties reference]: https://doc.arvados.org/api/properties.html
    """
    cumulative_cost: 'float'
    """A float with the estimated cost of all cloud instances used to run
    container(s) to fulfill this container request and their subrequests.
    The value is `0` if cost estimation is not available on this cluster.
    """
    output_glob: 'List'
    """An array of strings of shell-style glob patterns that define which file(s)
    and subdirectory(ies) under the `output_path` directory should be recorded in
    the container's final output. Refer to the [glob patterns reference][] for details.

    [glob patterns reference]: https://doc.arvados.org/api/methods/containers.html#glob_patterns
    """


class ContainerRequestList(TypedDict, total=False):
    """A list of ContainerRequest objects.

    This is the dictionary object returned when you call `ContainerRequests.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `ContainerRequest` objects.
    """
    kind: 'str' = 'arvados#containerRequestList'
    """Object type. Always arvados#containerRequestList."""
    etag: 'str'
    """List cache version."""
    items: 'List[ContainerRequest]'
    """An array of matching ContainerRequest objects."""


class ContainerRequests:
    """Methods to query and manipulate Arvados container requests"""

    def container_status(self, *, uuid: 'str') -> 'ArvadosAPIRequest[ContainerRequest]':
        """Return scheduling details for a container request.

        Required parameters:

        * uuid: str --- The UUID of the container request to query.
        """

    def create(self, *, body: "Dict[Literal['container_request'], ContainerRequest]", cluster_id: 'Optional[str]' = None, ensure_unique_name: 'bool' = False, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[ContainerRequest]':
        """Create a new ContainerRequest.

        Required parameters:

        * body: Dict[Literal['container_request'], ContainerRequest] --- A dictionary with a single item `'container_request'`.
          Its value is a `ContainerRequest` dictionary defining the attributes to set. 

        Optional parameters:

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster where this object should be created. 

        * ensure_unique_name: bool --- If the given name is already used by this owner, adjust the name to ensure uniqueness instead of returning an error. Default `False`.

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[ContainerRequest]':
        """Delete an existing ContainerRequest.

        Required parameters:

        * uuid: str --- The UUID of the ContainerRequest to delete.
        """

    def get(self, *, uuid: 'str', include_trash: 'bool' = False, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[ContainerRequest]':
        """Get a ContainerRequest record by UUID.

        Required parameters:

        * uuid: str --- The UUID of the ContainerRequest to return. 

        Optional parameters:

        * include_trash: bool --- Show container request even if its owner project is trashed. Default `False`.

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def list(self, *, bypass_federation: 'bool' = False, cluster_id: 'Optional[str]' = None, count: 'str' = 'exact', distinct: 'bool' = False, filters: 'Optional[List]' = None, include_trash: 'bool' = False, limit: 'int' = 100, offset: 'int' = 0, order: 'Optional[List]' = None, select: 'Optional[List]' = None, where: 'Optional[Dict[str, Any]]' = None) -> 'ArvadosAPIRequest[ContainerRequestList]':
        """Retrieve a ContainerRequestList.

        This method returns a single page of `ContainerRequest` objects that match your search
        criteria. If you just want to iterate all objects that match your search
        criteria, consider using `arvados.util.keyset_list_all`.

        Optional parameters:

        * bypass_federation: bool --- If true, do not return results from other clusters in the
          federation, only the cluster that received the request.
          You must be an administrator to use this flag. Default `False`.

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster to return objects from 

        * count: str --- A string to determine result counting behavior. Supported values are:

          * `"exact"`: The response will include an `items_available` field that
            counts the number of objects that matched this search criteria,
            including ones not included in `items`.

          * `"none"`: The response will not include an `items_avaliable`
            field. This improves performance by returning a result as soon as enough
            `items` have been loaded for this result.

          Default `'exact'`.

        * distinct: bool --- If this is true, and multiple objects have the same values
          for the attributes that you specify in the `select` parameter, then each unique
          set of values will only be returned once in the result set. Default `False`.

        * filters: Optional[List] --- Filters to limit which objects are returned by their attributes.
          Refer to the [filters reference][] for more information about how to write filters. 

          [filters reference]: https://doc.arvados.org/api/methods.html#filters

        * include_trash: bool --- Include container requests whose owner project is trashed. Default `False`.

        * limit: int --- The maximum number of objects to return in the result.
          Note that the API may return fewer results than this if your request hits other
          limits set by the administrator. Default `100`.

        * offset: int --- Return matching objects starting from this index.
          Note that result indexes may change if objects are modified in between a series
          of list calls. Default `0`.

        * order: Optional[List] --- An array of strings to set the order in which matching objects are returned.
          Each string has the format `<ATTRIBUTE> <DIRECTION>`.
          `DIRECTION` can be `asc` or omitted for ascending, or `desc` for descending. 

        * select: Optional[List] --- An array of names of attributes to return from each matching object. 

        * where: Optional[Dict[str, Any]] --- An object to limit which objects are returned by their attributes.
          The keys of this object are attribute names.
          Each value is either a single matching value or an array of matching values for that attribute.
          The `filters` parameter is more flexible and preferred.
        """

    def update(self, *, body: "Dict[Literal['container_request'], ContainerRequest]", uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[ContainerRequest]':
        """Update attributes of an existing ContainerRequest.

        Required parameters:

        * body: Dict[Literal['container_request'], ContainerRequest] --- A dictionary with a single item `'container_request'`.
          Its value is a `ContainerRequest` dictionary defining the attributes to set. 

        * uuid: str --- The UUID of the ContainerRequest to update. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """


class Container(TypedDict, total=False):
    """Arvados container record

    A container represents compute work that has been or should be dispatched,
    along with its results. A container can satisfy one or more container requests.

    This is the dictionary object that represents a single Container in Arvados
    and is returned by most `Containers` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    etag: 'str'
    """Object cache version."""
    uuid: 'str'
    """This container's Arvados UUID, like `zzzzz-dz642-12345abcde67890`."""
    owner_uuid: 'str'
    """The UUID of the user or group that owns this container."""
    created_at: 'str'
    """The time this container was created. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_at: 'str'
    """The time this container was last updated. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_user_uuid: 'str'
    """The UUID of the user that last updated this container."""
    state: 'str'
    """A string representing the container's current execution status. Possible
    values are:

      * `"Queued"` --- This container has not been dispatched yet.
      * `"Locked"` --- A dispatcher has claimed this container in preparation to run it.
      * `"Running"` --- A dispatcher is running this container.
      * `"Cancelled"` --- Container execution has been cancelled by user request.
      * `"Complete"` --- A dispatcher ran this container to completion and recorded the results.
    """
    started_at: 'str'
    """The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    finished_at: 'str'
    """The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    log: 'str'
    """The portable data hash of the Arvados collection that contains this
    container's logs.
    """
    environment: 'Dict[str, Any]'
    """A hash of string keys and values that defines the environment variables
    for the dispatcher to set when it executes this container.
    """
    cwd: 'str'
    """A string that the defines the working directory that the dispatcher should
    use when it executes the command inside this container.
    """
    command: 'List'
    """An array of strings that defines the command that the dispatcher should
    execute inside this container.
    """
    output_path: 'str'
    """A string that defines the file or directory path where the command
    writes output that should be saved from this container.
    """
    mounts: 'Dict[str, Any]'
    """A hash where each key names a directory inside this container, and its
    value is an object that defines the mount source for that directory. Refer
    to the [mount types reference][] for details.

    [mount types reference]: https://doc.arvados.org/api/methods/containers.html#mount_types
    """
    runtime_constraints: 'Dict[str, Any]'
    """A hash that identifies compute resources this container requires to run
    successfully. See the [runtime constraints reference][] for details.

    [runtime constraints reference]: https://doc.arvados.org/api/methods/containers.html#runtime_constraints
    """
    output: 'str'
    """The portable data hash of the Arvados collection that contains this
    container's output file(s).
    """
    container_image: 'str'
    """The portable data hash of the Arvados collection that contains the image
    to use for this container.
    """
    progress: 'float'
    """A float between 0.0 and 1.0 (inclusive) that represents the container's
    execution progress. This attribute is not implemented yet.
    """
    priority: 'int'
    """An integer between 0 and 1000 (inclusive) that represents this container's
    scheduling priority. 0 represents a request to be cancelled. Higher
    values represent higher priority. Refer to the [priority reference][] for details.

    [priority reference]: https://doc.arvados.org/api/methods/container_requests.html#priority
    """
    exit_code: 'int'
    """An integer that records the Unix exit code of the `command` from a
    finished container.
    """
    auth_uuid: 'str'
    """The UUID of the Arvados API client authorization token that a dispatcher
    should use to set up this container. This token is automatically created by
    Arvados and this attribute automatically assigned unless a container is
    created with `runtime_token`.
    """
    locked_by_uuid: 'str'
    """The UUID of the Arvados API client authorization token that successfully
    locked this container in preparation to execute it.
    """
    scheduling_parameters: 'Dict[str, Any]'
    """A hash of scheduling parameters that should be passed to the underlying
    dispatcher when this container is run.
    See the [scheduling parameters reference][] for details.

    [scheduling parameters reference]: https://doc.arvados.org/api/methods/containers.html#scheduling_parameters
    """
    runtime_status: 'Dict[str, Any]'
    """A hash with status updates from a running container.
    Refer to the [runtime status reference][] for details.

    [runtime status reference]: https://doc.arvados.org/api/methods/containers.html#runtime_status
    """
    runtime_user_uuid: 'str'
    """The UUID of the Arvados user associated with the API client authorization
    token used to run this container.
    """
    runtime_auth_scopes: 'List'
    """The `scopes` from the API client authorization token used to run this container."""
    lock_count: 'int'
    """The number of times this container has been locked by a dispatcher. This
    may be greater than 1 if a dispatcher locks a container but then execution is
    interrupted for any reason.
    """
    gateway_address: 'str'
    """A string with the address of the Arvados gateway server, in `HOST:PORT`
    format. This is for internal use only.
    """
    interactive_session_started: 'bool'
    """This flag is set true if any user starts an interactive shell inside the
    running container.
    """
    output_storage_classes: 'List'
    """An array of strings identifying the storage class(es) that should be set
    on the output collection of this container. Storage classes are configured by
    the cluster administrator.
    """
    output_properties: 'Dict[str, Any]'
    """A hash of arbitrary metadata to set on the output collection of this container.
    Some keys may be reserved by Arvados or defined by a configured vocabulary.
    Refer to the [metadata properties reference][] for details.

    [metadata properties reference]: https://doc.arvados.org/api/properties.html
    """
    cost: 'float'
    """A float with the estimated cost of the cloud instance used to run this
    container. The value is `0` if cost estimation is not available on this cluster.
    """
    subrequests_cost: 'float'
    """A float with the estimated cost of all cloud instances used to run this
    container and all its subrequests. The value is `0` if cost estimation is not
    available on this cluster.
    """
    output_glob: 'List'
    """An array of strings of shell-style glob patterns that define which file(s)
    and subdirectory(ies) under the `output_path` directory should be recorded in
    the container's final output. Refer to the [glob patterns reference][] for details.

    [glob patterns reference]: https://doc.arvados.org/api/methods/containers.html#glob_patterns
    """


class ContainerList(TypedDict, total=False):
    """A list of Container objects.

    This is the dictionary object returned when you call `Containers.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `Container` objects.
    """
    kind: 'str' = 'arvados#containerList'
    """Object type. Always arvados#containerList."""
    etag: 'str'
    """List cache version."""
    items: 'List[Container]'
    """An array of matching Container objects."""


class Containers:
    """Methods to query and manipulate Arvados containers"""

    def auth(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Container]':
        """Get the API client authorization token associated with this container.

        Required parameters:

        * uuid: str --- The UUID of the Container to query.
        """

    def create(self, *, body: "Dict[Literal['container'], Container]", cluster_id: 'Optional[str]' = None, ensure_unique_name: 'bool' = False, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[Container]':
        """Create a new Container.

        Required parameters:

        * body: Dict[Literal['container'], Container] --- A dictionary with a single item `'container'`.
          Its value is a `Container` dictionary defining the attributes to set. 

        Optional parameters:

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster where this object should be created. 

        * ensure_unique_name: bool --- If the given name is already used by this owner, adjust the name to ensure uniqueness instead of returning an error. Default `False`.

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def current(self) -> 'ArvadosAPIRequest[Container]':
        """Return the container record associated with the API token authorizing this request."""

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Container]':
        """Delete an existing Container.

        Required parameters:

        * uuid: str --- The UUID of the Container to delete.
        """

    def get(self, *, uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[Container]':
        """Get a Container record by UUID.

        Required parameters:

        * uuid: str --- The UUID of the Container to return. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def list(self, *, bypass_federation: 'bool' = False, cluster_id: 'Optional[str]' = None, count: 'str' = 'exact', distinct: 'bool' = False, filters: 'Optional[List]' = None, limit: 'int' = 100, offset: 'int' = 0, order: 'Optional[List]' = None, select: 'Optional[List]' = None, where: 'Optional[Dict[str, Any]]' = None) -> 'ArvadosAPIRequest[ContainerList]':
        """Retrieve a ContainerList.

        This method returns a single page of `Container` objects that match your search
        criteria. If you just want to iterate all objects that match your search
        criteria, consider using `arvados.util.keyset_list_all`.

        Optional parameters:

        * bypass_federation: bool --- If true, do not return results from other clusters in the
          federation, only the cluster that received the request.
          You must be an administrator to use this flag. Default `False`.

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster to return objects from 

        * count: str --- A string to determine result counting behavior. Supported values are:

          * `"exact"`: The response will include an `items_available` field that
            counts the number of objects that matched this search criteria,
            including ones not included in `items`.

          * `"none"`: The response will not include an `items_avaliable`
            field. This improves performance by returning a result as soon as enough
            `items` have been loaded for this result.

          Default `'exact'`.

        * distinct: bool --- If this is true, and multiple objects have the same values
          for the attributes that you specify in the `select` parameter, then each unique
          set of values will only be returned once in the result set. Default `False`.

        * filters: Optional[List] --- Filters to limit which objects are returned by their attributes.
          Refer to the [filters reference][] for more information about how to write filters. 

          [filters reference]: https://doc.arvados.org/api/methods.html#filters

        * limit: int --- The maximum number of objects to return in the result.
          Note that the API may return fewer results than this if your request hits other
          limits set by the administrator. Default `100`.

        * offset: int --- Return matching objects starting from this index.
          Note that result indexes may change if objects are modified in between a series
          of list calls. Default `0`.

        * order: Optional[List] --- An array of strings to set the order in which matching objects are returned.
          Each string has the format `<ATTRIBUTE> <DIRECTION>`.
          `DIRECTION` can be `asc` or omitted for ascending, or `desc` for descending. 

        * select: Optional[List] --- An array of names of attributes to return from each matching object. 

        * where: Optional[Dict[str, Any]] --- An object to limit which objects are returned by their attributes.
          The keys of this object are attribute names.
          Each value is either a single matching value or an array of matching values for that attribute.
          The `filters` parameter is more flexible and preferred.
        """

    def lock(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Container]':
        """Lock a container (for a dispatcher to begin running it).

        Required parameters:

        * uuid: str --- The UUID of the Container to update.
        """

    def secret_mounts(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Container]':
        """Return secret mount information for the container associated with the API token authorizing this request.

        Required parameters:

        * uuid: str --- The UUID of the Container to query.
        """

    def unlock(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Container]':
        """Unlock a container (for a dispatcher to stop running it).

        Required parameters:

        * uuid: str --- The UUID of the Container to update.
        """

    def update(self, *, body: "Dict[Literal['container'], Container]", uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[Container]':
        """Update attributes of an existing Container.

        Required parameters:

        * body: Dict[Literal['container'], Container] --- A dictionary with a single item `'container'`.
          Its value is a `Container` dictionary defining the attributes to set. 

        * uuid: str --- The UUID of the Container to update. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def update_priority(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Container]':
        """Recalculate and return the priority of a given container.

        Required parameters:

        * uuid: str --- The UUID of the Container to update.
        """


class Group(TypedDict, total=False):
    """Arvados group

    Groups provide a way to organize users or data together, depending on their
    `group_class`.

    This is the dictionary object that represents a single Group in Arvados
    and is returned by most `Groups` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    etag: 'str'
    """Object cache version."""
    uuid: 'str'
    """This group's Arvados UUID, like `zzzzz-j7d0g-12345abcde67890`."""
    owner_uuid: 'str'
    """The UUID of the user or group that owns this group."""
    created_at: 'str'
    """The time this group was created. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_user_uuid: 'str'
    """The UUID of the user that last updated this group."""
    modified_at: 'str'
    """The time this group was last updated. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    name: 'str'
    """The name of this group assigned by a user."""
    description: 'str'
    """A longer HTML description of this group assigned by a user.
    Allowed HTML tags are `a`, `b`, `blockquote`, `br`, `code`,
    `del`, `dd`, `dl`, `dt`, `em`, `h1`, `h2`, `h3`, `h4`, `h5`, `h6`, `hr`,
    `i`, `img`, `kbd`, `li`, `ol`, `p`, `pre`,
    `s`, `section`, `span`, `strong`, `sub`, `sup`, and `ul`.
    """
    group_class: 'str'
    """A string representing which type of group this is. One of:

      * `"filter"` --- A virtual project whose contents are selected dynamically by filters.
      * `"project"` --- An Arvados project that can contain collections,
        container records, workflows, and subprojects.
      * `"role"` --- A group of users that can be granted permissions in Arvados.
    """
    trash_at: 'str'
    """The time this group will be trashed. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    is_trashed: 'bool'
    """A boolean flag to indicate whether or not this group is trashed."""
    delete_at: 'str'
    """The time this group will be permanently deleted. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    properties: 'Dict[str, Any]'
    """A hash of arbitrary metadata for this group.
    Some keys may be reserved by Arvados or defined by a configured vocabulary.
    Refer to the [metadata properties reference][] for details.

    [metadata properties reference]: https://doc.arvados.org/api/properties.html
    """
    frozen_by_uuid: 'str'
    """The UUID of the user that has frozen this group, if any. Frozen projects
    cannot have their contents or metadata changed, even by admins.
    """


class GroupList(TypedDict, total=False):
    """A list of Group objects.

    This is the dictionary object returned when you call `Groups.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `Group` objects.
    """
    kind: 'str' = 'arvados#groupList'
    """Object type. Always arvados#groupList."""
    etag: 'str'
    """List cache version."""
    items: 'List[Group]'
    """An array of matching Group objects."""


class Groups:
    """Methods to query and manipulate Arvados groups"""

    def contents(self, *, bypass_federation: 'bool' = False, cluster_id: 'Optional[str]' = None, count: 'str' = 'exact', distinct: 'bool' = False, exclude_home_project: 'bool' = False, filters: 'Optional[List]' = None, include: 'Optional[List]' = None, include_old_versions: 'bool' = False, include_trash: 'bool' = False, limit: 'int' = 100, offset: 'int' = 0, order: 'Optional[List]' = None, recursive: 'bool' = False, select: 'Optional[List]' = None, uuid: 'str' = '', where: 'Optional[Dict[str, Any]]' = None) -> 'ArvadosAPIRequest[Group]':
        """List objects that belong to a group.

        Optional parameters:

        * bypass_federation: bool --- If true, do not return results from other clusters in the
          federation, only the cluster that received the request.
          You must be an administrator to use this flag. Default `False`.

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster to return objects from 

        * count: str --- A string to determine result counting behavior. Supported values are:

          * `"exact"`: The response will include an `items_available` field that
            counts the number of objects that matched this search criteria,
            including ones not included in `items`.

          * `"none"`: The response will not include an `items_avaliable`
            field. This improves performance by returning a result as soon as enough
            `items` have been loaded for this result.

          Default `'exact'`.

        * distinct: bool --- If this is true, and multiple objects have the same values
          for the attributes that you specify in the `select` parameter, then each unique
          set of values will only be returned once in the result set. Default `False`.

        * exclude_home_project: bool --- If true, exclude contents of the user's home project from the listing.
          Calling this method with this flag set is how clients enumerate objects shared
          with the current user. Default `False`.

        * filters: Optional[List] --- Filters to limit which objects are returned by their attributes.
          Refer to the [filters reference][] for more information about how to write filters. 

          [filters reference]: https://doc.arvados.org/api/methods.html#filters

        * include: Optional[List] --- An array of referenced objects to include in the `included` field of the response. Supported values in the array are:

          * `"container_uuid"`
          * `"owner_uuid"`



        * include_old_versions: bool --- If true, include past versions of collections in the listing. Default `False`.

        * include_trash: bool --- Include items whose `is_trashed` attribute is true. Default `False`.

        * limit: int --- The maximum number of objects to return in the result.
          Note that the API may return fewer results than this if your request hits other
          limits set by the administrator. Default `100`.

        * offset: int --- Return matching objects starting from this index.
          Note that result indexes may change if objects are modified in between a series
          of list calls. Default `0`.

        * order: Optional[List] --- An array of strings to set the order in which matching objects are returned.
          Each string has the format `<ATTRIBUTE> <DIRECTION>`.
          `DIRECTION` can be `asc` or omitted for ascending, or `desc` for descending. 

        * recursive: bool --- If true, include contents from child groups recursively. Default `False`.

        * select: Optional[List] --- An array of names of attributes to return from each matching object. 

        * uuid: str --- If given, limit the listing to objects owned by the
          user or group with this UUID. Default `''`.

        * where: Optional[Dict[str, Any]] --- An object to limit which objects are returned by their attributes.
          The keys of this object are attribute names.
          Each value is either a single matching value or an array of matching values for that attribute.
          The `filters` parameter is more flexible and preferred.
        """

    def create(self, *, body: "Dict[Literal['group'], Group]", async_: 'bool' = False, cluster_id: 'Optional[str]' = None, ensure_unique_name: 'bool' = False, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[Group]':
        """Create a new Group.

        Required parameters:

        * body: Dict[Literal['group'], Group] --- A dictionary with a single item `'group'`.
          Its value is a `Group` dictionary defining the attributes to set. 

        Optional parameters:

        * async: bool --- If true, cluster permission will not be updated immediately, but instead at the next configured update interval. Default `False`.

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster where this object should be created. 

        * ensure_unique_name: bool --- If the given name is already used by this owner, adjust the name to ensure uniqueness instead of returning an error. Default `False`.

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Group]':
        """Delete an existing Group.

        Required parameters:

        * uuid: str --- The UUID of the Group to delete.
        """

    def get(self, *, uuid: 'str', include_trash: 'bool' = False, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[Group]':
        """Get a Group record by UUID.

        Required parameters:

        * uuid: str --- The UUID of the Group to return. 

        Optional parameters:

        * include_trash: bool --- Return group/project even if its `is_trashed` attribute is true. Default `False`.

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def list(self, *, bypass_federation: 'bool' = False, cluster_id: 'Optional[str]' = None, count: 'str' = 'exact', distinct: 'bool' = False, filters: 'Optional[List]' = None, include_trash: 'bool' = False, limit: 'int' = 100, offset: 'int' = 0, order: 'Optional[List]' = None, select: 'Optional[List]' = None, where: 'Optional[Dict[str, Any]]' = None) -> 'ArvadosAPIRequest[GroupList]':
        """Retrieve a GroupList.

        This method returns a single page of `Group` objects that match your search
        criteria. If you just want to iterate all objects that match your search
        criteria, consider using `arvados.util.keyset_list_all`.

        Optional parameters:

        * bypass_federation: bool --- If true, do not return results from other clusters in the
          federation, only the cluster that received the request.
          You must be an administrator to use this flag. Default `False`.

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster to return objects from 

        * count: str --- A string to determine result counting behavior. Supported values are:

          * `"exact"`: The response will include an `items_available` field that
            counts the number of objects that matched this search criteria,
            including ones not included in `items`.

          * `"none"`: The response will not include an `items_avaliable`
            field. This improves performance by returning a result as soon as enough
            `items` have been loaded for this result.

          Default `'exact'`.

        * distinct: bool --- If this is true, and multiple objects have the same values
          for the attributes that you specify in the `select` parameter, then each unique
          set of values will only be returned once in the result set. Default `False`.

        * filters: Optional[List] --- Filters to limit which objects are returned by their attributes.
          Refer to the [filters reference][] for more information about how to write filters. 

          [filters reference]: https://doc.arvados.org/api/methods.html#filters

        * include_trash: bool --- Include items whose `is_trashed` attribute is true. Default `False`.

        * limit: int --- The maximum number of objects to return in the result.
          Note that the API may return fewer results than this if your request hits other
          limits set by the administrator. Default `100`.

        * offset: int --- Return matching objects starting from this index.
          Note that result indexes may change if objects are modified in between a series
          of list calls. Default `0`.

        * order: Optional[List] --- An array of strings to set the order in which matching objects are returned.
          Each string has the format `<ATTRIBUTE> <DIRECTION>`.
          `DIRECTION` can be `asc` or omitted for ascending, or `desc` for descending. 

        * select: Optional[List] --- An array of names of attributes to return from each matching object. 

        * where: Optional[Dict[str, Any]] --- An object to limit which objects are returned by their attributes.
          The keys of this object are attribute names.
          Each value is either a single matching value or an array of matching values for that attribute.
          The `filters` parameter is more flexible and preferred.
        """

    def shared(self, *, bypass_federation: 'bool' = False, cluster_id: 'Optional[str]' = None, count: 'str' = 'exact', distinct: 'bool' = False, filters: 'Optional[List]' = None, include: 'Optional[str]' = None, include_trash: 'bool' = False, limit: 'int' = 100, offset: 'int' = 0, order: 'Optional[List]' = None, select: 'Optional[List]' = None, where: 'Optional[Dict[str, Any]]' = None) -> 'ArvadosAPIRequest[Group]':
        """List groups that the current user can access via permission links.

        Optional parameters:

        * bypass_federation: bool --- If true, do not return results from other clusters in the
          federation, only the cluster that received the request.
          You must be an administrator to use this flag. Default `False`.

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster to return objects from 

        * count: str --- A string to determine result counting behavior. Supported values are:

          * `"exact"`: The response will include an `items_available` field that
            counts the number of objects that matched this search criteria,
            including ones not included in `items`.

          * `"none"`: The response will not include an `items_avaliable`
            field. This improves performance by returning a result as soon as enough
            `items` have been loaded for this result.

          Default `'exact'`.

        * distinct: bool --- If this is true, and multiple objects have the same values
          for the attributes that you specify in the `select` parameter, then each unique
          set of values will only be returned once in the result set. Default `False`.

        * filters: Optional[List] --- Filters to limit which objects are returned by their attributes.
          Refer to the [filters reference][] for more information about how to write filters. 

          [filters reference]: https://doc.arvados.org/api/methods.html#filters

        * include: Optional[str] --- A string naming referenced objects to include in the `included` field of the response. Supported values are:

          * `"owner_uuid"`



        * include_trash: bool --- Include items whose `is_trashed` attribute is true. Default `False`.

        * limit: int --- The maximum number of objects to return in the result.
          Note that the API may return fewer results than this if your request hits other
          limits set by the administrator. Default `100`.

        * offset: int --- Return matching objects starting from this index.
          Note that result indexes may change if objects are modified in between a series
          of list calls. Default `0`.

        * order: Optional[List] --- An array of strings to set the order in which matching objects are returned.
          Each string has the format `<ATTRIBUTE> <DIRECTION>`.
          `DIRECTION` can be `asc` or omitted for ascending, or `desc` for descending. 

        * select: Optional[List] --- An array of names of attributes to return from each matching object. 

        * where: Optional[Dict[str, Any]] --- An object to limit which objects are returned by their attributes.
          The keys of this object are attribute names.
          Each value is either a single matching value or an array of matching values for that attribute.
          The `filters` parameter is more flexible and preferred.
        """

    def trash(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Group]':
        """Trash a group.

        Required parameters:

        * uuid: str --- The UUID of the Group to update.
        """

    def untrash(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Group]':
        """Untrash a group.

        Required parameters:

        * uuid: str --- The UUID of the Group to update.
        """

    def update(self, *, body: "Dict[Literal['group'], Group]", uuid: 'str', async_: 'bool' = False, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[Group]':
        """Update attributes of an existing Group.

        Required parameters:

        * body: Dict[Literal['group'], Group] --- A dictionary with a single item `'group'`.
          Its value is a `Group` dictionary defining the attributes to set. 

        * uuid: str --- The UUID of the Group to update. 

        Optional parameters:

        * async: bool --- If true, cluster permission will not be updated immediately, but instead at the next configured update interval. Default `False`.

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """


class KeepService(TypedDict, total=False):
    """Arvados Keep service

    This resource stores information about a single Keep service in this Arvados
    cluster that clients can contact to retrieve and store data.

    This is the dictionary object that represents a single KeepService in Arvados
    and is returned by most `KeepServices` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    etag: 'str'
    """Object cache version."""
    uuid: 'str'
    """This Keep service's Arvados UUID, like `zzzzz-bi6l4-12345abcde67890`."""
    owner_uuid: 'str'
    """The UUID of the user or group that owns this Keep service."""
    modified_by_user_uuid: 'str'
    """The UUID of the user that last updated this Keep service."""
    modified_at: 'str'
    """The time this Keep service was last updated. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    service_host: 'str'
    """The DNS hostname of this Keep service."""
    service_port: 'int'
    """The TCP port where this Keep service listens."""
    service_ssl_flag: 'bool'
    """A boolean flag that indicates whether or not this Keep service uses TLS/SSL."""
    service_type: 'str'
    """A string that describes which type of Keep service this is. One of:

      * `"disk"` --- A service that stores blocks on a local filesystem.
      * `"blob"` --- A service that stores blocks in a cloud object store.
      * `"proxy"` --- A keepproxy service.
    """
    created_at: 'str'
    """The time this Keep service was created. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    read_only: 'bool'
    """A boolean flag. If set, this Keep service does not accept requests to write data
    blocks; it only serves blocks it already has.
    """


class KeepServiceList(TypedDict, total=False):
    """A list of KeepService objects.

    This is the dictionary object returned when you call `KeepServices.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `KeepService` objects.
    """
    kind: 'str' = 'arvados#keepServiceList'
    """Object type. Always arvados#keepServiceList."""
    etag: 'str'
    """List cache version."""
    items: 'List[KeepService]'
    """An array of matching KeepService objects."""


class KeepServices:
    """Methods to query and manipulate Arvados keep services"""

    def accessible(self) -> 'ArvadosAPIRequest[KeepService]':
        """List Keep services that the current client can access."""

    def create(self, *, body: "Dict[Literal['keep_service'], KeepService]", cluster_id: 'Optional[str]' = None, ensure_unique_name: 'bool' = False, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[KeepService]':
        """Create a new KeepService.

        Required parameters:

        * body: Dict[Literal['keep_service'], KeepService] --- A dictionary with a single item `'keep_service'`.
          Its value is a `KeepService` dictionary defining the attributes to set. 

        Optional parameters:

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster where this object should be created. 

        * ensure_unique_name: bool --- If the given name is already used by this owner, adjust the name to ensure uniqueness instead of returning an error. Default `False`.

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[KeepService]':
        """Delete an existing KeepService.

        Required parameters:

        * uuid: str --- The UUID of the KeepService to delete.
        """

    def get(self, *, uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[KeepService]':
        """Get a KeepService record by UUID.

        Required parameters:

        * uuid: str --- The UUID of the KeepService to return. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def list(self, *, bypass_federation: 'bool' = False, cluster_id: 'Optional[str]' = None, count: 'str' = 'exact', distinct: 'bool' = False, filters: 'Optional[List]' = None, limit: 'int' = 100, offset: 'int' = 0, order: 'Optional[List]' = None, select: 'Optional[List]' = None, where: 'Optional[Dict[str, Any]]' = None) -> 'ArvadosAPIRequest[KeepServiceList]':
        """Retrieve a KeepServiceList.

        This method returns a single page of `KeepService` objects that match your search
        criteria. If you just want to iterate all objects that match your search
        criteria, consider using `arvados.util.keyset_list_all`.

        Optional parameters:

        * bypass_federation: bool --- If true, do not return results from other clusters in the
          federation, only the cluster that received the request.
          You must be an administrator to use this flag. Default `False`.

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster to return objects from 

        * count: str --- A string to determine result counting behavior. Supported values are:

          * `"exact"`: The response will include an `items_available` field that
            counts the number of objects that matched this search criteria,
            including ones not included in `items`.

          * `"none"`: The response will not include an `items_avaliable`
            field. This improves performance by returning a result as soon as enough
            `items` have been loaded for this result.

          Default `'exact'`.

        * distinct: bool --- If this is true, and multiple objects have the same values
          for the attributes that you specify in the `select` parameter, then each unique
          set of values will only be returned once in the result set. Default `False`.

        * filters: Optional[List] --- Filters to limit which objects are returned by their attributes.
          Refer to the [filters reference][] for more information about how to write filters. 

          [filters reference]: https://doc.arvados.org/api/methods.html#filters

        * limit: int --- The maximum number of objects to return in the result.
          Note that the API may return fewer results than this if your request hits other
          limits set by the administrator. Default `100`.

        * offset: int --- Return matching objects starting from this index.
          Note that result indexes may change if objects are modified in between a series
          of list calls. Default `0`.

        * order: Optional[List] --- An array of strings to set the order in which matching objects are returned.
          Each string has the format `<ATTRIBUTE> <DIRECTION>`.
          `DIRECTION` can be `asc` or omitted for ascending, or `desc` for descending. 

        * select: Optional[List] --- An array of names of attributes to return from each matching object. 

        * where: Optional[Dict[str, Any]] --- An object to limit which objects are returned by their attributes.
          The keys of this object are attribute names.
          Each value is either a single matching value or an array of matching values for that attribute.
          The `filters` parameter is more flexible and preferred.
        """

    def update(self, *, body: "Dict[Literal['keep_service'], KeepService]", uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[KeepService]':
        """Update attributes of an existing KeepService.

        Required parameters:

        * body: Dict[Literal['keep_service'], KeepService] --- A dictionary with a single item `'keep_service'`.
          Its value is a `KeepService` dictionary defining the attributes to set. 

        * uuid: str --- The UUID of the KeepService to update. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """


class Link(TypedDict, total=False):
    """Arvados object link

    A link provides a way to define relationships between Arvados objects,
    depending on their `link_class`.

    This is the dictionary object that represents a single Link in Arvados
    and is returned by most `Links` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    etag: 'str'
    """Object cache version."""
    uuid: 'str'
    """This link's Arvados UUID, like `zzzzz-o0j2j-12345abcde67890`."""
    owner_uuid: 'str'
    """The UUID of the user or group that owns this link."""
    created_at: 'str'
    """The time this link was created. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_user_uuid: 'str'
    """The UUID of the user that last updated this link."""
    modified_at: 'str'
    """The time this link was last updated. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    tail_uuid: 'str'
    """The UUID of the Arvados object that is the target of this relationship."""
    link_class: 'str'
    """A string that defines which kind of link this is. One of:

      * `"permission"` --- This link grants a permission to the user or group
        referenced by `head_uuid` to the object referenced by `tail_uuid`. The
        access level is set by `name`.
      * `"star"` --- This link represents a "favorite." The user referenced
        by `head_uuid` wants quick access to the object referenced by `tail_uuid`.
      * `"tag"` --- This link represents an unstructured metadata tag. The object
        referenced by `tail_uuid` has the tag defined by `name`.
    """
    name: 'str'
    """The primary value of this link. For `"permission"` links, this is one of
    `"can_read"`, `"can_write"`, or `"can_manage"`.
    """
    head_uuid: 'str'
    """The UUID of the Arvados object that is the originator or actor in this
    relationship. May be null.
    """
    properties: 'Dict[str, Any]'
    """A hash of arbitrary metadata for this link.
    Some keys may be reserved by Arvados or defined by a configured vocabulary.
    Refer to the [metadata properties reference][] for details.

    [metadata properties reference]: https://doc.arvados.org/api/properties.html
    """


class LinkList(TypedDict, total=False):
    """A list of Link objects.

    This is the dictionary object returned when you call `Links.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `Link` objects.
    """
    kind: 'str' = 'arvados#linkList'
    """Object type. Always arvados#linkList."""
    etag: 'str'
    """List cache version."""
    items: 'List[Link]'
    """An array of matching Link objects."""


class Links:
    """Methods to query and manipulate Arvados links"""

    def create(self, *, body: "Dict[Literal['link'], Link]", cluster_id: 'Optional[str]' = None, ensure_unique_name: 'bool' = False, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[Link]':
        """Create a new Link.

        Required parameters:

        * body: Dict[Literal['link'], Link] --- A dictionary with a single item `'link'`.
          Its value is a `Link` dictionary defining the attributes to set. 

        Optional parameters:

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster where this object should be created. 

        * ensure_unique_name: bool --- If the given name is already used by this owner, adjust the name to ensure uniqueness instead of returning an error. Default `False`.

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Link]':
        """Delete an existing Link.

        Required parameters:

        * uuid: str --- The UUID of the Link to delete.
        """

    def get(self, *, uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[Link]':
        """Get a Link record by UUID.

        Required parameters:

        * uuid: str --- The UUID of the Link to return. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def get_permissions(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Link]':
        """List permissions granted on an Arvados object.

        Required parameters:

        * uuid: str --- The UUID of the Link to query.
        """

    def list(self, *, bypass_federation: 'bool' = False, cluster_id: 'Optional[str]' = None, count: 'str' = 'exact', distinct: 'bool' = False, filters: 'Optional[List]' = None, limit: 'int' = 100, offset: 'int' = 0, order: 'Optional[List]' = None, select: 'Optional[List]' = None, where: 'Optional[Dict[str, Any]]' = None) -> 'ArvadosAPIRequest[LinkList]':
        """Retrieve a LinkList.

        This method returns a single page of `Link` objects that match your search
        criteria. If you just want to iterate all objects that match your search
        criteria, consider using `arvados.util.keyset_list_all`.

        Optional parameters:

        * bypass_federation: bool --- If true, do not return results from other clusters in the
          federation, only the cluster that received the request.
          You must be an administrator to use this flag. Default `False`.

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster to return objects from 

        * count: str --- A string to determine result counting behavior. Supported values are:

          * `"exact"`: The response will include an `items_available` field that
            counts the number of objects that matched this search criteria,
            including ones not included in `items`.

          * `"none"`: The response will not include an `items_avaliable`
            field. This improves performance by returning a result as soon as enough
            `items` have been loaded for this result.

          Default `'exact'`.

        * distinct: bool --- If this is true, and multiple objects have the same values
          for the attributes that you specify in the `select` parameter, then each unique
          set of values will only be returned once in the result set. Default `False`.

        * filters: Optional[List] --- Filters to limit which objects are returned by their attributes.
          Refer to the [filters reference][] for more information about how to write filters. 

          [filters reference]: https://doc.arvados.org/api/methods.html#filters

        * limit: int --- The maximum number of objects to return in the result.
          Note that the API may return fewer results than this if your request hits other
          limits set by the administrator. Default `100`.

        * offset: int --- Return matching objects starting from this index.
          Note that result indexes may change if objects are modified in between a series
          of list calls. Default `0`.

        * order: Optional[List] --- An array of strings to set the order in which matching objects are returned.
          Each string has the format `<ATTRIBUTE> <DIRECTION>`.
          `DIRECTION` can be `asc` or omitted for ascending, or `desc` for descending. 

        * select: Optional[List] --- An array of names of attributes to return from each matching object. 

        * where: Optional[Dict[str, Any]] --- An object to limit which objects are returned by their attributes.
          The keys of this object are attribute names.
          Each value is either a single matching value or an array of matching values for that attribute.
          The `filters` parameter is more flexible and preferred.
        """

    def update(self, *, body: "Dict[Literal['link'], Link]", uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[Link]':
        """Update attributes of an existing Link.

        Required parameters:

        * body: Dict[Literal['link'], Link] --- A dictionary with a single item `'link'`.
          Its value is a `Link` dictionary defining the attributes to set. 

        * uuid: str --- The UUID of the Link to update. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """


class Log(TypedDict, total=False):
    """Arvados log record

    This resource represents a single log record about an event in this Arvados
    cluster. Some individual Arvados services create log records. Users can also
    create custom logs.

    This is the dictionary object that represents a single Log in Arvados
    and is returned by most `Logs` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    etag: 'str'
    """Object cache version."""
    id: 'int'
    """The serial number of this log. You can use this in filters to query logs
    that were created before/after another.
    """
    uuid: 'str'
    """This log's Arvados UUID, like `zzzzz-57u5n-12345abcde67890`."""
    owner_uuid: 'str'
    """The UUID of the user or group that owns this log."""
    modified_by_user_uuid: 'str'
    """The UUID of the user that last updated this log."""
    object_uuid: 'str'
    """The UUID of the Arvados object that this log pertains to, such as a user
    or container.
    """
    event_at: 'str'
    """The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    event_type: 'str'
    """An arbitrary short string that classifies what type of log this is."""
    summary: 'str'
    """A text string that describes the logged event. This is the primary
    attribute for simple logs.
    """
    properties: 'Dict[str, Any]'
    """A hash of arbitrary metadata for this log.
    Some keys may be reserved by Arvados or defined by a configured vocabulary.
    Refer to the [metadata properties reference][] for details.

    [metadata properties reference]: https://doc.arvados.org/api/properties.html
    """
    created_at: 'str'
    """The time this log was created. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_at: 'str'
    """The time this log was last updated. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    object_owner_uuid: 'str'
    """The `owner_uuid` of the object referenced by `object_uuid` at the time
    this log was created.
    """


class LogList(TypedDict, total=False):
    """A list of Log objects.

    This is the dictionary object returned when you call `Logs.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `Log` objects.
    """
    kind: 'str' = 'arvados#logList'
    """Object type. Always arvados#logList."""
    etag: 'str'
    """List cache version."""
    items: 'List[Log]'
    """An array of matching Log objects."""


class Logs:
    """Methods to query and manipulate Arvados logs"""

    def create(self, *, body: "Dict[Literal['log'], Log]", cluster_id: 'Optional[str]' = None, ensure_unique_name: 'bool' = False, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[Log]':
        """Create a new Log.

        Required parameters:

        * body: Dict[Literal['log'], Log] --- A dictionary with a single item `'log'`.
          Its value is a `Log` dictionary defining the attributes to set. 

        Optional parameters:

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster where this object should be created. 

        * ensure_unique_name: bool --- If the given name is already used by this owner, adjust the name to ensure uniqueness instead of returning an error. Default `False`.

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Log]':
        """Delete an existing Log.

        Required parameters:

        * uuid: str --- The UUID of the Log to delete.
        """

    def get(self, *, uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[Log]':
        """Get a Log record by UUID.

        Required parameters:

        * uuid: str --- The UUID of the Log to return. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def list(self, *, bypass_federation: 'bool' = False, cluster_id: 'Optional[str]' = None, count: 'str' = 'exact', distinct: 'bool' = False, filters: 'Optional[List]' = None, limit: 'int' = 100, offset: 'int' = 0, order: 'Optional[List]' = None, select: 'Optional[List]' = None, where: 'Optional[Dict[str, Any]]' = None) -> 'ArvadosAPIRequest[LogList]':
        """Retrieve a LogList.

        This method returns a single page of `Log` objects that match your search
        criteria. If you just want to iterate all objects that match your search
        criteria, consider using `arvados.util.keyset_list_all`.

        Optional parameters:

        * bypass_federation: bool --- If true, do not return results from other clusters in the
          federation, only the cluster that received the request.
          You must be an administrator to use this flag. Default `False`.

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster to return objects from 

        * count: str --- A string to determine result counting behavior. Supported values are:

          * `"exact"`: The response will include an `items_available` field that
            counts the number of objects that matched this search criteria,
            including ones not included in `items`.

          * `"none"`: The response will not include an `items_avaliable`
            field. This improves performance by returning a result as soon as enough
            `items` have been loaded for this result.

          Default `'exact'`.

        * distinct: bool --- If this is true, and multiple objects have the same values
          for the attributes that you specify in the `select` parameter, then each unique
          set of values will only be returned once in the result set. Default `False`.

        * filters: Optional[List] --- Filters to limit which objects are returned by their attributes.
          Refer to the [filters reference][] for more information about how to write filters. 

          [filters reference]: https://doc.arvados.org/api/methods.html#filters

        * limit: int --- The maximum number of objects to return in the result.
          Note that the API may return fewer results than this if your request hits other
          limits set by the administrator. Default `100`.

        * offset: int --- Return matching objects starting from this index.
          Note that result indexes may change if objects are modified in between a series
          of list calls. Default `0`.

        * order: Optional[List] --- An array of strings to set the order in which matching objects are returned.
          Each string has the format `<ATTRIBUTE> <DIRECTION>`.
          `DIRECTION` can be `asc` or omitted for ascending, or `desc` for descending. 

        * select: Optional[List] --- An array of names of attributes to return from each matching object. 

        * where: Optional[Dict[str, Any]] --- An object to limit which objects are returned by their attributes.
          The keys of this object are attribute names.
          Each value is either a single matching value or an array of matching values for that attribute.
          The `filters` parameter is more flexible and preferred.
        """

    def update(self, *, body: "Dict[Literal['log'], Log]", uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[Log]':
        """Update attributes of an existing Log.

        Required parameters:

        * body: Dict[Literal['log'], Log] --- A dictionary with a single item `'log'`.
          Its value is a `Log` dictionary defining the attributes to set. 

        * uuid: str --- The UUID of the Log to update. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """


class Sys:
    """Methods to query and manipulate Arvados sys"""

    def get(self) -> 'ArvadosAPIRequest[Dict[str, Any]]':
        """Run scheduled data trash and sweep operations across this cluster's Keep services."""


class UserAgreement(TypedDict, total=False):
    """Arvados user agreement

    A user agreement is a collection with terms that users must agree to before
    they can use this Arvados cluster.

    This is the dictionary object that represents a single UserAgreement in Arvados
    and is returned by most `UserAgreements` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    etag: 'str'
    """Object cache version."""
    owner_uuid: 'str'
    """The UUID of the user or group that owns this user agreement."""
    created_at: 'str'
    """The time this user agreement was created. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_user_uuid: 'str'
    """The UUID of the user that last updated this user agreement."""
    modified_at: 'str'
    """The time this user agreement was last updated. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    portable_data_hash: 'str'
    """The portable data hash of this user agreement. This string provides a unique
    and stable reference to these contents.
    """
    replication_desired: 'int'
    """The number of copies that should be made for data in this user agreement."""
    replication_confirmed_at: 'str'
    """The last time the cluster confirmed that it met `replication_confirmed`
    for this user agreement. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`.
    """
    replication_confirmed: 'int'
    """The number of copies of data in this user agreement that the cluster has confirmed
    exist in storage.
    """
    uuid: 'str'
    """This user agreement's Arvados UUID, like `zzzzz-gv0sa-12345abcde67890`."""
    manifest_text: 'str'
    """The manifest text that describes how files are constructed from data blocks
    in this user agreement. Refer to the [manifest format][] reference for details.

    [manifest format]: https://doc.arvados.org/architecture/manifest-format.html
    """
    name: 'str'
    """The name of this user agreement assigned by a user."""
    description: 'str'
    """A longer HTML description of this user agreement assigned by a user.
    Allowed HTML tags are `a`, `b`, `blockquote`, `br`, `code`,
    `del`, `dd`, `dl`, `dt`, `em`, `h1`, `h2`, `h3`, `h4`, `h5`, `h6`, `hr`,
    `i`, `img`, `kbd`, `li`, `ol`, `p`, `pre`,
    `s`, `section`, `span`, `strong`, `sub`, `sup`, and `ul`.
    """
    properties: 'Dict[str, Any]'
    """A hash of arbitrary metadata for this user agreement.
    Some keys may be reserved by Arvados or defined by a configured vocabulary.
    Refer to the [metadata properties reference][] for details.

    [metadata properties reference]: https://doc.arvados.org/api/properties.html
    """
    delete_at: 'str'
    """The time this user agreement will be permanently deleted. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    trash_at: 'str'
    """The time this user agreement will be trashed. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    is_trashed: 'bool'
    """A boolean flag to indicate whether or not this user agreement is trashed."""
    storage_classes_desired: 'List'
    """An array of strings identifying the storage class(es) that should be used
    for data in this user agreement. Storage classes are configured by the cluster administrator.
    """
    storage_classes_confirmed: 'List'
    """An array of strings identifying the storage class(es) the cluster has
    confirmed have a copy of this user agreement's data.
    """
    storage_classes_confirmed_at: 'str'
    """The last time the cluster confirmed that data was stored on the storage
    class(es) in `storage_classes_confirmed`. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`.
    """
    current_version_uuid: 'str'
    """The UUID of the current version of this user agreement."""
    version: 'int'
    """An integer that counts which version of a user agreement this record
    represents. Refer to [collection versioning][] for details. This attribute is
    read-only.

    [collection versioning]: https://doc.arvados.org/user/topics/collection-versioning.html
    """
    preserve_version: 'bool'
    """A boolean flag to indicate whether this specific version of this user agreement
    should be persisted in cluster storage.
    """
    file_count: 'int'
    """The number of files represented in this user agreement's `manifest_text`.
    This attribute is read-only.
    """
    file_size_total: 'int'
    """The total size in bytes of files represented in this user agreement's `manifest_text`.
    This attribute is read-only.
    """


class UserAgreementList(TypedDict, total=False):
    """A list of UserAgreement objects.

    This is the dictionary object returned when you call `UserAgreements.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `UserAgreement` objects.
    """
    kind: 'str' = 'arvados#userAgreementList'
    """Object type. Always arvados#userAgreementList."""
    etag: 'str'
    """List cache version."""
    items: 'List[UserAgreement]'
    """An array of matching UserAgreement objects."""


class UserAgreements:
    """Methods to query and manipulate Arvados user agreements"""

    def create(self, *, body: "Dict[Literal['user_agreement'], UserAgreement]", cluster_id: 'Optional[str]' = None, ensure_unique_name: 'bool' = False, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[UserAgreement]':
        """Create a new UserAgreement.

        Required parameters:

        * body: Dict[Literal['user_agreement'], UserAgreement] --- A dictionary with a single item `'user_agreement'`.
          Its value is a `UserAgreement` dictionary defining the attributes to set. 

        Optional parameters:

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster where this object should be created. 

        * ensure_unique_name: bool --- If the given name is already used by this owner, adjust the name to ensure uniqueness instead of returning an error. Default `False`.

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[UserAgreement]':
        """Delete an existing UserAgreement.

        Required parameters:

        * uuid: str --- The UUID of the UserAgreement to delete.
        """

    def get(self, *, uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[UserAgreement]':
        """Get a UserAgreement record by UUID.

        Required parameters:

        * uuid: str --- The UUID of the UserAgreement to return. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def list(self, *, bypass_federation: 'bool' = False, cluster_id: 'Optional[str]' = None, count: 'str' = 'exact', distinct: 'bool' = False, filters: 'Optional[List]' = None, limit: 'int' = 100, offset: 'int' = 0, order: 'Optional[List]' = None, select: 'Optional[List]' = None, where: 'Optional[Dict[str, Any]]' = None) -> 'ArvadosAPIRequest[UserAgreementList]':
        """Retrieve a UserAgreementList.

        This method returns a single page of `UserAgreement` objects that match your search
        criteria. If you just want to iterate all objects that match your search
        criteria, consider using `arvados.util.keyset_list_all`.

        Optional parameters:

        * bypass_federation: bool --- If true, do not return results from other clusters in the
          federation, only the cluster that received the request.
          You must be an administrator to use this flag. Default `False`.

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster to return objects from 

        * count: str --- A string to determine result counting behavior. Supported values are:

          * `"exact"`: The response will include an `items_available` field that
            counts the number of objects that matched this search criteria,
            including ones not included in `items`.

          * `"none"`: The response will not include an `items_avaliable`
            field. This improves performance by returning a result as soon as enough
            `items` have been loaded for this result.

          Default `'exact'`.

        * distinct: bool --- If this is true, and multiple objects have the same values
          for the attributes that you specify in the `select` parameter, then each unique
          set of values will only be returned once in the result set. Default `False`.

        * filters: Optional[List] --- Filters to limit which objects are returned by their attributes.
          Refer to the [filters reference][] for more information about how to write filters. 

          [filters reference]: https://doc.arvados.org/api/methods.html#filters

        * limit: int --- The maximum number of objects to return in the result.
          Note that the API may return fewer results than this if your request hits other
          limits set by the administrator. Default `100`.

        * offset: int --- Return matching objects starting from this index.
          Note that result indexes may change if objects are modified in between a series
          of list calls. Default `0`.

        * order: Optional[List] --- An array of strings to set the order in which matching objects are returned.
          Each string has the format `<ATTRIBUTE> <DIRECTION>`.
          `DIRECTION` can be `asc` or omitted for ascending, or `desc` for descending. 

        * select: Optional[List] --- An array of names of attributes to return from each matching object. 

        * where: Optional[Dict[str, Any]] --- An object to limit which objects are returned by their attributes.
          The keys of this object are attribute names.
          Each value is either a single matching value or an array of matching values for that attribute.
          The `filters` parameter is more flexible and preferred.
        """

    def sign(self) -> 'ArvadosAPIRequest[UserAgreement]':
        """Create a signature link from the current user for a given user agreement."""

    def signatures(self) -> 'ArvadosAPIRequest[UserAgreement]':
        """List all user agreement signature links from a user."""

    def update(self, *, body: "Dict[Literal['user_agreement'], UserAgreement]", uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[UserAgreement]':
        """Update attributes of an existing UserAgreement.

        Required parameters:

        * body: Dict[Literal['user_agreement'], UserAgreement] --- A dictionary with a single item `'user_agreement'`.
          Its value is a `UserAgreement` dictionary defining the attributes to set. 

        * uuid: str --- The UUID of the UserAgreement to update. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """


class User(TypedDict, total=False):
    """Arvados user

    A user represents a single individual or role who may be authorized to access
    this Arvados cluster.

    This is the dictionary object that represents a single User in Arvados
    and is returned by most `Users` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    etag: 'str'
    """Object cache version."""
    uuid: 'str'
    """This user's Arvados UUID, like `zzzzz-tpzed-12345abcde67890`."""
    owner_uuid: 'str'
    """The UUID of the user or group that owns this user."""
    created_at: 'str'
    """The time this user was created. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_user_uuid: 'str'
    """The UUID of the user that last updated this user."""
    modified_at: 'str'
    """The time this user was last updated. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    email: 'str'
    """This user's email address."""
    first_name: 'str'
    """This user's first name."""
    last_name: 'str'
    """This user's last name."""
    identity_url: 'str'
    """A URL that represents this user with the cluster's identity provider."""
    is_admin: 'bool'
    """A boolean flag. If set, this user is an administrator of the Arvados
    cluster, and automatically passes most permissions checks.
    """
    prefs: 'Dict[str, Any]'
    """A hash that stores cluster-wide user preferences."""
    is_active: 'bool'
    """A boolean flag. If unset, this user is not permitted to make any Arvados
    API requests.
    """
    username: 'str'
    """This user's Unix username on virtual machines."""


class UserList(TypedDict, total=False):
    """A list of User objects.

    This is the dictionary object returned when you call `Users.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `User` objects.
    """
    kind: 'str' = 'arvados#userList'
    """Object type. Always arvados#userList."""
    etag: 'str'
    """List cache version."""
    items: 'List[User]'
    """An array of matching User objects."""


class Users:
    """Methods to query and manipulate Arvados users"""

    def activate(self, *, uuid: 'str') -> 'ArvadosAPIRequest[User]':
        """Set the `is_active` flag on a user record.

        Required parameters:

        * uuid: str --- The UUID of the User to update.
        """

    def create(self, *, body: "Dict[Literal['user'], User]", cluster_id: 'Optional[str]' = None, ensure_unique_name: 'bool' = False, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[User]':
        """Create a new User.

        Required parameters:

        * body: Dict[Literal['user'], User] --- A dictionary with a single item `'user'`.
          Its value is a `User` dictionary defining the attributes to set. 

        Optional parameters:

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster where this object should be created. 

        * ensure_unique_name: bool --- If the given name is already used by this owner, adjust the name to ensure uniqueness instead of returning an error. Default `False`.

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def current(self) -> 'ArvadosAPIRequest[User]':
        """Return the user record associated with the API token authorizing this request."""

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[User]':
        """Delete an existing User.

        Required parameters:

        * uuid: str --- The UUID of the User to delete.
        """

    def get(self, *, uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[User]':
        """Get a User record by UUID.

        Required parameters:

        * uuid: str --- The UUID of the User to return. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def list(self, *, bypass_federation: 'bool' = False, cluster_id: 'Optional[str]' = None, count: 'str' = 'exact', distinct: 'bool' = False, filters: 'Optional[List]' = None, limit: 'int' = 100, offset: 'int' = 0, order: 'Optional[List]' = None, select: 'Optional[List]' = None, where: 'Optional[Dict[str, Any]]' = None) -> 'ArvadosAPIRequest[UserList]':
        """Retrieve a UserList.

        This method returns a single page of `User` objects that match your search
        criteria. If you just want to iterate all objects that match your search
        criteria, consider using `arvados.util.keyset_list_all`.

        Optional parameters:

        * bypass_federation: bool --- If true, do not return results from other clusters in the
          federation, only the cluster that received the request.
          You must be an administrator to use this flag. Default `False`.

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster to return objects from 

        * count: str --- A string to determine result counting behavior. Supported values are:

          * `"exact"`: The response will include an `items_available` field that
            counts the number of objects that matched this search criteria,
            including ones not included in `items`.

          * `"none"`: The response will not include an `items_avaliable`
            field. This improves performance by returning a result as soon as enough
            `items` have been loaded for this result.

          Default `'exact'`.

        * distinct: bool --- If this is true, and multiple objects have the same values
          for the attributes that you specify in the `select` parameter, then each unique
          set of values will only be returned once in the result set. Default `False`.

        * filters: Optional[List] --- Filters to limit which objects are returned by their attributes.
          Refer to the [filters reference][] for more information about how to write filters. 

          [filters reference]: https://doc.arvados.org/api/methods.html#filters

        * limit: int --- The maximum number of objects to return in the result.
          Note that the API may return fewer results than this if your request hits other
          limits set by the administrator. Default `100`.

        * offset: int --- Return matching objects starting from this index.
          Note that result indexes may change if objects are modified in between a series
          of list calls. Default `0`.

        * order: Optional[List] --- An array of strings to set the order in which matching objects are returned.
          Each string has the format `<ATTRIBUTE> <DIRECTION>`.
          `DIRECTION` can be `asc` or omitted for ascending, or `desc` for descending. 

        * select: Optional[List] --- An array of names of attributes to return from each matching object. 

        * where: Optional[Dict[str, Any]] --- An object to limit which objects are returned by their attributes.
          The keys of this object are attribute names.
          Each value is either a single matching value or an array of matching values for that attribute.
          The `filters` parameter is more flexible and preferred.
        """

    def merge(self, *, new_owner_uuid: 'str', new_user_token: 'Optional[str]' = None, new_user_uuid: 'Optional[str]' = None, old_user_uuid: 'Optional[str]' = None, redirect_to_new_user: 'bool' = False) -> 'ArvadosAPIRequest[User]':
        """Transfer ownership of one user's data to another.

        Required parameters:

        * new_owner_uuid: str --- UUID of the user or group that will take ownership of data owned by the old user. 

        Optional parameters:

        * new_user_token: Optional[str] --- Valid API token for the user receiving ownership. If you use this option, it takes ownership of data owned by the user making the request. 

        * new_user_uuid: Optional[str] --- UUID of the user receiving ownership. You must be an admin to use this option. 

        * old_user_uuid: Optional[str] --- UUID of the user whose ownership is being transferred to `new_owner_uuid`. You must be an admin to use this option. 

        * redirect_to_new_user: bool --- If true, authorization attempts for the old user will be redirected to the new user. Default `False`.
        """

    def setup(self, *, repo_name: 'Optional[str]' = None, send_notification_email: 'bool' = False, user: 'Optional[Dict[str, Any]]' = None, uuid: 'Optional[str]' = None, vm_uuid: 'Optional[str]' = None) -> 'ArvadosAPIRequest[User]':
        """Convenience method to "fully" set up a user record with a virtual machine login and notification email.

        Optional parameters:

        * repo_name: Optional[str] --- This parameter is obsolete and ignored. 

        * send_notification_email: bool --- If true, send an email to the user notifying them they can now access this Arvados cluster. Default `False`.

        * user: Optional[Dict[str, Any]] --- Attributes of a new user record to set up. 

        * uuid: Optional[str] --- UUID of an existing user record to set up. 

        * vm_uuid: Optional[str] --- If given, setup creates a login link to allow this user to access the Arvados virtual machine with this UUID.
        """

    def system(self) -> 'ArvadosAPIRequest[User]':
        """Return this cluster's system ("root") user record."""

    def unsetup(self, *, uuid: 'str') -> 'ArvadosAPIRequest[User]':
        """Unset a user's active flag and delete associated records.

        Required parameters:

        * uuid: str --- The UUID of the User to update.
        """

    def update(self, *, body: "Dict[Literal['user'], User]", uuid: 'str', bypass_federation: 'bool' = False, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[User]':
        """Update attributes of an existing User.

        Required parameters:

        * body: Dict[Literal['user'], User] --- A dictionary with a single item `'user'`.
          Its value is a `User` dictionary defining the attributes to set. 

        * uuid: str --- The UUID of the User to update. 

        Optional parameters:

        * bypass_federation: bool --- If true, do not try to update the user on any other clusters in the federation,
          only the cluster that received the request.
          You must be an administrator to use this flag. Default `False`.

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """


class VirtualMachine(TypedDict, total=False):
    """Arvados virtual machine ("shell node")

    This resource stores information about a virtual machine or "shell node"
    hosted on this Arvados cluster where users can log in and use preconfigured
    Arvados client tools.

    This is the dictionary object that represents a single VirtualMachine in Arvados
    and is returned by most `VirtualMachines` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    etag: 'str'
    """Object cache version."""
    uuid: 'str'
    """This virtual machine's Arvados UUID, like `zzzzz-2x53u-12345abcde67890`."""
    owner_uuid: 'str'
    """The UUID of the user or group that owns this virtual machine."""
    modified_by_user_uuid: 'str'
    """The UUID of the user that last updated this virtual machine."""
    modified_at: 'str'
    """The time this virtual machine was last updated. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    hostname: 'str'
    """The DNS hostname where users should access this virtual machine."""
    created_at: 'str'
    """The time this virtual machine was created. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""


class VirtualMachineList(TypedDict, total=False):
    """A list of VirtualMachine objects.

    This is the dictionary object returned when you call `VirtualMachines.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `VirtualMachine` objects.
    """
    kind: 'str' = 'arvados#virtualMachineList'
    """Object type. Always arvados#virtualMachineList."""
    etag: 'str'
    """List cache version."""
    items: 'List[VirtualMachine]'
    """An array of matching VirtualMachine objects."""


class VirtualMachines:
    """Methods to query and manipulate Arvados virtual machines"""

    def create(self, *, body: "Dict[Literal['virtual_machine'], VirtualMachine]", cluster_id: 'Optional[str]' = None, ensure_unique_name: 'bool' = False, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[VirtualMachine]':
        """Create a new VirtualMachine.

        Required parameters:

        * body: Dict[Literal['virtual_machine'], VirtualMachine] --- A dictionary with a single item `'virtual_machine'`.
          Its value is a `VirtualMachine` dictionary defining the attributes to set. 

        Optional parameters:

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster where this object should be created. 

        * ensure_unique_name: bool --- If the given name is already used by this owner, adjust the name to ensure uniqueness instead of returning an error. Default `False`.

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[VirtualMachine]':
        """Delete an existing VirtualMachine.

        Required parameters:

        * uuid: str --- The UUID of the VirtualMachine to delete.
        """

    def get(self, *, uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[VirtualMachine]':
        """Get a VirtualMachine record by UUID.

        Required parameters:

        * uuid: str --- The UUID of the VirtualMachine to return. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def get_all_logins(self) -> 'ArvadosAPIRequest[VirtualMachine]':
        """List login permission links for all virtual machines."""

    def list(self, *, bypass_federation: 'bool' = False, cluster_id: 'Optional[str]' = None, count: 'str' = 'exact', distinct: 'bool' = False, filters: 'Optional[List]' = None, limit: 'int' = 100, offset: 'int' = 0, order: 'Optional[List]' = None, select: 'Optional[List]' = None, where: 'Optional[Dict[str, Any]]' = None) -> 'ArvadosAPIRequest[VirtualMachineList]':
        """Retrieve a VirtualMachineList.

        This method returns a single page of `VirtualMachine` objects that match your search
        criteria. If you just want to iterate all objects that match your search
        criteria, consider using `arvados.util.keyset_list_all`.

        Optional parameters:

        * bypass_federation: bool --- If true, do not return results from other clusters in the
          federation, only the cluster that received the request.
          You must be an administrator to use this flag. Default `False`.

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster to return objects from 

        * count: str --- A string to determine result counting behavior. Supported values are:

          * `"exact"`: The response will include an `items_available` field that
            counts the number of objects that matched this search criteria,
            including ones not included in `items`.

          * `"none"`: The response will not include an `items_avaliable`
            field. This improves performance by returning a result as soon as enough
            `items` have been loaded for this result.

          Default `'exact'`.

        * distinct: bool --- If this is true, and multiple objects have the same values
          for the attributes that you specify in the `select` parameter, then each unique
          set of values will only be returned once in the result set. Default `False`.

        * filters: Optional[List] --- Filters to limit which objects are returned by their attributes.
          Refer to the [filters reference][] for more information about how to write filters. 

          [filters reference]: https://doc.arvados.org/api/methods.html#filters

        * limit: int --- The maximum number of objects to return in the result.
          Note that the API may return fewer results than this if your request hits other
          limits set by the administrator. Default `100`.

        * offset: int --- Return matching objects starting from this index.
          Note that result indexes may change if objects are modified in between a series
          of list calls. Default `0`.

        * order: Optional[List] --- An array of strings to set the order in which matching objects are returned.
          Each string has the format `<ATTRIBUTE> <DIRECTION>`.
          `DIRECTION` can be `asc` or omitted for ascending, or `desc` for descending. 

        * select: Optional[List] --- An array of names of attributes to return from each matching object. 

        * where: Optional[Dict[str, Any]] --- An object to limit which objects are returned by their attributes.
          The keys of this object are attribute names.
          Each value is either a single matching value or an array of matching values for that attribute.
          The `filters` parameter is more flexible and preferred.
        """

    def logins(self, *, uuid: 'str') -> 'ArvadosAPIRequest[VirtualMachine]':
        """List login permission links for a given virtual machine.

        Required parameters:

        * uuid: str --- The UUID of the VirtualMachine to query.
        """

    def update(self, *, body: "Dict[Literal['virtual_machine'], VirtualMachine]", uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[VirtualMachine]':
        """Update attributes of an existing VirtualMachine.

        Required parameters:

        * body: Dict[Literal['virtual_machine'], VirtualMachine] --- A dictionary with a single item `'virtual_machine'`.
          Its value is a `VirtualMachine` dictionary defining the attributes to set. 

        * uuid: str --- The UUID of the VirtualMachine to update. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """


class Vocabularies:
    """Methods to query and manipulate Arvados vocabularies"""

    def get(self) -> 'ArvadosAPIRequest[Dict[str, Any]]':
        """Get this cluster's configured vocabulary definition.

        Refer to [metadata vocabulary documentation][] for details.

        [metadata vocabulary documentation]: https://doc.aravdos.org/admin/metadata-vocabulary.html
        """


class Workflow(TypedDict, total=False):
    """Arvados workflow

    A workflow contains workflow definition source code that Arvados can execute
    along with associated metadata for users.

    This is the dictionary object that represents a single Workflow in Arvados
    and is returned by most `Workflows` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    etag: 'str'
    """Object cache version."""
    uuid: 'str'
    """This workflow's Arvados UUID, like `zzzzz-7fd4e-12345abcde67890`."""
    owner_uuid: 'str'
    """The UUID of the user or group that owns this workflow."""
    created_at: 'str'
    """The time this workflow was created. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_at: 'str'
    """The time this workflow was last updated. The string encodes a UTC date and time in ISO 8601 format. Pass this to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_user_uuid: 'str'
    """The UUID of the user that last updated this workflow."""
    name: 'str'
    """The name of this workflow assigned by a user."""
    description: 'str'
    """A longer HTML description of this workflow assigned by a user.
    Allowed HTML tags are `a`, `b`, `blockquote`, `br`, `code`,
    `del`, `dd`, `dl`, `dt`, `em`, `h1`, `h2`, `h3`, `h4`, `h5`, `h6`, `hr`,
    `i`, `img`, `kbd`, `li`, `ol`, `p`, `pre`,
    `s`, `section`, `span`, `strong`, `sub`, `sup`, and `ul`.
    """
    definition: 'str'
    """A string with the CWL source of this workflow."""


class WorkflowList(TypedDict, total=False):
    """A list of Workflow objects.

    This is the dictionary object returned when you call `Workflows.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `Workflow` objects.
    """
    kind: 'str' = 'arvados#workflowList'
    """Object type. Always arvados#workflowList."""
    etag: 'str'
    """List cache version."""
    items: 'List[Workflow]'
    """An array of matching Workflow objects."""


class Workflows:
    """Methods to query and manipulate Arvados workflows"""

    def create(self, *, body: "Dict[Literal['workflow'], Workflow]", cluster_id: 'Optional[str]' = None, ensure_unique_name: 'bool' = False, select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[Workflow]':
        """Create a new Workflow.

        Required parameters:

        * body: Dict[Literal['workflow'], Workflow] --- A dictionary with a single item `'workflow'`.
          Its value is a `Workflow` dictionary defining the attributes to set. 

        Optional parameters:

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster where this object should be created. 

        * ensure_unique_name: bool --- If the given name is already used by this owner, adjust the name to ensure uniqueness instead of returning an error. Default `False`.

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Workflow]':
        """Delete an existing Workflow.

        Required parameters:

        * uuid: str --- The UUID of the Workflow to delete.
        """

    def get(self, *, uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[Workflow]':
        """Get a Workflow record by UUID.

        Required parameters:

        * uuid: str --- The UUID of the Workflow to return. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """

    def list(self, *, bypass_federation: 'bool' = False, cluster_id: 'Optional[str]' = None, count: 'str' = 'exact', distinct: 'bool' = False, filters: 'Optional[List]' = None, limit: 'int' = 100, offset: 'int' = 0, order: 'Optional[List]' = None, select: 'Optional[List]' = None, where: 'Optional[Dict[str, Any]]' = None) -> 'ArvadosAPIRequest[WorkflowList]':
        """Retrieve a WorkflowList.

        This method returns a single page of `Workflow` objects that match your search
        criteria. If you just want to iterate all objects that match your search
        criteria, consider using `arvados.util.keyset_list_all`.

        Optional parameters:

        * bypass_federation: bool --- If true, do not return results from other clusters in the
          federation, only the cluster that received the request.
          You must be an administrator to use this flag. Default `False`.

        * cluster_id: Optional[str] --- Cluster ID of a federated cluster to return objects from 

        * count: str --- A string to determine result counting behavior. Supported values are:

          * `"exact"`: The response will include an `items_available` field that
            counts the number of objects that matched this search criteria,
            including ones not included in `items`.

          * `"none"`: The response will not include an `items_avaliable`
            field. This improves performance by returning a result as soon as enough
            `items` have been loaded for this result.

          Default `'exact'`.

        * distinct: bool --- If this is true, and multiple objects have the same values
          for the attributes that you specify in the `select` parameter, then each unique
          set of values will only be returned once in the result set. Default `False`.

        * filters: Optional[List] --- Filters to limit which objects are returned by their attributes.
          Refer to the [filters reference][] for more information about how to write filters. 

          [filters reference]: https://doc.arvados.org/api/methods.html#filters

        * limit: int --- The maximum number of objects to return in the result.
          Note that the API may return fewer results than this if your request hits other
          limits set by the administrator. Default `100`.

        * offset: int --- Return matching objects starting from this index.
          Note that result indexes may change if objects are modified in between a series
          of list calls. Default `0`.

        * order: Optional[List] --- An array of strings to set the order in which matching objects are returned.
          Each string has the format `<ATTRIBUTE> <DIRECTION>`.
          `DIRECTION` can be `asc` or omitted for ascending, or `desc` for descending. 

        * select: Optional[List] --- An array of names of attributes to return from each matching object. 

        * where: Optional[Dict[str, Any]] --- An object to limit which objects are returned by their attributes.
          The keys of this object are attribute names.
          Each value is either a single matching value or an array of matching values for that attribute.
          The `filters` parameter is more flexible and preferred.
        """

    def update(self, *, body: "Dict[Literal['workflow'], Workflow]", uuid: 'str', select: 'Optional[List]' = None) -> 'ArvadosAPIRequest[Workflow]':
        """Update attributes of an existing Workflow.

        Required parameters:

        * body: Dict[Literal['workflow'], Workflow] --- A dictionary with a single item `'workflow'`.
          Its value is a `Workflow` dictionary defining the attributes to set. 

        * uuid: str --- The UUID of the Workflow to update. 

        Optional parameters:

        * select: Optional[List] --- An array of names of attributes to return in the response.
        """


class ArvadosAPIClient(googleapiclient.discovery.Resource):

    def api_client_authorizations(self) -> 'ApiClientAuthorizations':
        """Return an instance of `ApiClientAuthorizations` to call methods via this client"""

    def authorized_keys(self) -> 'AuthorizedKeys':
        """Return an instance of `AuthorizedKeys` to call methods via this client"""

    def collections(self) -> 'Collections':
        """Return an instance of `Collections` to call methods via this client"""

    def computed_permissions(self) -> 'ComputedPermissions':
        """Return an instance of `ComputedPermissions` to call methods via this client"""

    def configs(self) -> 'Configs':
        """Return an instance of `Configs` to call methods via this client"""

    def container_requests(self) -> 'ContainerRequests':
        """Return an instance of `ContainerRequests` to call methods via this client"""

    def containers(self) -> 'Containers':
        """Return an instance of `Containers` to call methods via this client"""

    def groups(self) -> 'Groups':
        """Return an instance of `Groups` to call methods via this client"""

    def keep_services(self) -> 'KeepServices':
        """Return an instance of `KeepServices` to call methods via this client"""

    def links(self) -> 'Links':
        """Return an instance of `Links` to call methods via this client"""

    def logs(self) -> 'Logs':
        """Return an instance of `Logs` to call methods via this client"""

    def sys(self) -> 'Sys':
        """Return an instance of `Sys` to call methods via this client"""

    def user_agreements(self) -> 'UserAgreements':
        """Return an instance of `UserAgreements` to call methods via this client"""

    def users(self) -> 'Users':
        """Return an instance of `Users` to call methods via this client"""

    def virtual_machines(self) -> 'VirtualMachines':
        """Return an instance of `VirtualMachines` to call methods via this client"""

    def vocabularies(self) -> 'Vocabularies':
        """Return an instance of `Vocabularies` to call methods via this client"""

    def workflows(self) -> 'Workflows':
        """Return an instance of `Workflows` to call methods via this client"""
