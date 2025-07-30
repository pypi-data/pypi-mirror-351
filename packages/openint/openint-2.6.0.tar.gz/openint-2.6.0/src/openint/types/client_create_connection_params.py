# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo
from .oauth_connection_settings_param import OAuthConnectionSettingsParam

__all__ = [
    "ClientCreateConnectionParams",
    "Data",
    "DataConnectorAcceloDiscriminatedConnectionSettings",
    "DataConnectorAcceloDiscriminatedConnectionSettingsSettings",
    "DataConnectorAcmeOauth2DiscriminatedConnectionSettings",
    "DataConnectorAcmeOauth2DiscriminatedConnectionSettingsSettings",
    "DataConnectorAdobeDiscriminatedConnectionSettings",
    "DataConnectorAdobeDiscriminatedConnectionSettingsSettings",
    "DataConnectorAdyenDiscriminatedConnectionSettings",
    "DataConnectorAdyenDiscriminatedConnectionSettingsSettings",
    "DataConnectorAircallDiscriminatedConnectionSettings",
    "DataConnectorAircallDiscriminatedConnectionSettingsSettings",
    "DataConnectorAmazonDiscriminatedConnectionSettings",
    "DataConnectorAmazonDiscriminatedConnectionSettingsSettings",
    "DataConnectorApaleoDiscriminatedConnectionSettings",
    "DataConnectorApaleoDiscriminatedConnectionSettingsSettings",
    "DataConnectorAsanaDiscriminatedConnectionSettings",
    "DataConnectorAsanaDiscriminatedConnectionSettingsSettings",
    "DataConnectorAttioDiscriminatedConnectionSettings",
    "DataConnectorAttioDiscriminatedConnectionSettingsSettings",
    "DataConnectorAuth0DiscriminatedConnectionSettings",
    "DataConnectorAuth0DiscriminatedConnectionSettingsSettings",
    "DataConnectorAutodeskDiscriminatedConnectionSettings",
    "DataConnectorAutodeskDiscriminatedConnectionSettingsSettings",
    "DataConnectorAwsDiscriminatedConnectionSettings",
    "DataConnectorAwsDiscriminatedConnectionSettingsSettings",
    "DataConnectorBamboohrDiscriminatedConnectionSettings",
    "DataConnectorBamboohrDiscriminatedConnectionSettingsSettings",
    "DataConnectorBasecampDiscriminatedConnectionSettings",
    "DataConnectorBasecampDiscriminatedConnectionSettingsSettings",
    "DataConnectorBattlenetDiscriminatedConnectionSettings",
    "DataConnectorBattlenetDiscriminatedConnectionSettingsSettings",
    "DataConnectorBigcommerceDiscriminatedConnectionSettings",
    "DataConnectorBigcommerceDiscriminatedConnectionSettingsSettings",
    "DataConnectorBitbucketDiscriminatedConnectionSettings",
    "DataConnectorBitbucketDiscriminatedConnectionSettingsSettings",
    "DataConnectorBitlyDiscriminatedConnectionSettings",
    "DataConnectorBitlyDiscriminatedConnectionSettingsSettings",
    "DataConnectorBlackbaudDiscriminatedConnectionSettings",
    "DataConnectorBlackbaudDiscriminatedConnectionSettingsSettings",
    "DataConnectorBoldsignDiscriminatedConnectionSettings",
    "DataConnectorBoldsignDiscriminatedConnectionSettingsSettings",
    "DataConnectorBoxDiscriminatedConnectionSettings",
    "DataConnectorBoxDiscriminatedConnectionSettingsSettings",
    "DataConnectorBraintreeDiscriminatedConnectionSettings",
    "DataConnectorBraintreeDiscriminatedConnectionSettingsSettings",
    "DataConnectorCalendlyDiscriminatedConnectionSettings",
    "DataConnectorCalendlyDiscriminatedConnectionSettingsSettings",
    "DataConnectorClickupDiscriminatedConnectionSettings",
    "DataConnectorClickupDiscriminatedConnectionSettingsSettings",
    "DataConnectorCloseDiscriminatedConnectionSettings",
    "DataConnectorCloseDiscriminatedConnectionSettingsSettings",
    "DataConnectorConfluenceDiscriminatedConnectionSettings",
    "DataConnectorConfluenceDiscriminatedConnectionSettingsSettings",
    "DataConnectorContentfulDiscriminatedConnectionSettings",
    "DataConnectorContentfulDiscriminatedConnectionSettingsSettings",
    "DataConnectorContentstackDiscriminatedConnectionSettings",
    "DataConnectorContentstackDiscriminatedConnectionSettingsSettings",
    "DataConnectorCopperDiscriminatedConnectionSettings",
    "DataConnectorCopperDiscriminatedConnectionSettingsSettings",
    "DataConnectorCorosDiscriminatedConnectionSettings",
    "DataConnectorCorosDiscriminatedConnectionSettingsSettings",
    "DataConnectorDatevDiscriminatedConnectionSettings",
    "DataConnectorDatevDiscriminatedConnectionSettingsSettings",
    "DataConnectorDeelDiscriminatedConnectionSettings",
    "DataConnectorDeelDiscriminatedConnectionSettingsSettings",
    "DataConnectorDialpadDiscriminatedConnectionSettings",
    "DataConnectorDialpadDiscriminatedConnectionSettingsSettings",
    "DataConnectorDigitaloceanDiscriminatedConnectionSettings",
    "DataConnectorDigitaloceanDiscriminatedConnectionSettingsSettings",
    "DataConnectorDiscordDiscriminatedConnectionSettings",
    "DataConnectorDiscordDiscriminatedConnectionSettingsSettings",
    "DataConnectorDocusignDiscriminatedConnectionSettings",
    "DataConnectorDocusignDiscriminatedConnectionSettingsSettings",
    "DataConnectorDropboxDiscriminatedConnectionSettings",
    "DataConnectorDropboxDiscriminatedConnectionSettingsSettings",
    "DataConnectorEbayDiscriminatedConnectionSettings",
    "DataConnectorEbayDiscriminatedConnectionSettingsSettings",
    "DataConnectorEgnyteDiscriminatedConnectionSettings",
    "DataConnectorEgnyteDiscriminatedConnectionSettingsSettings",
    "DataConnectorEnvoyDiscriminatedConnectionSettings",
    "DataConnectorEnvoyDiscriminatedConnectionSettingsSettings",
    "DataConnectorEventbriteDiscriminatedConnectionSettings",
    "DataConnectorEventbriteDiscriminatedConnectionSettingsSettings",
    "DataConnectorExistDiscriminatedConnectionSettings",
    "DataConnectorExistDiscriminatedConnectionSettingsSettings",
    "DataConnectorFacebookDiscriminatedConnectionSettings",
    "DataConnectorFacebookDiscriminatedConnectionSettingsSettings",
    "DataConnectorFactorialDiscriminatedConnectionSettings",
    "DataConnectorFactorialDiscriminatedConnectionSettingsSettings",
    "DataConnectorFigmaDiscriminatedConnectionSettings",
    "DataConnectorFigmaDiscriminatedConnectionSettingsSettings",
    "DataConnectorFitbitDiscriminatedConnectionSettings",
    "DataConnectorFitbitDiscriminatedConnectionSettingsSettings",
    "DataConnectorFortnoxDiscriminatedConnectionSettings",
    "DataConnectorFortnoxDiscriminatedConnectionSettingsSettings",
    "DataConnectorFreshbooksDiscriminatedConnectionSettings",
    "DataConnectorFreshbooksDiscriminatedConnectionSettingsSettings",
    "DataConnectorFrontDiscriminatedConnectionSettings",
    "DataConnectorFrontDiscriminatedConnectionSettingsSettings",
    "DataConnectorGitHubDiscriminatedConnectionSettings",
    "DataConnectorGitHubDiscriminatedConnectionSettingsSettings",
    "DataConnectorGitlabDiscriminatedConnectionSettings",
    "DataConnectorGitlabDiscriminatedConnectionSettingsSettings",
    "DataConnectorGongDiscriminatedConnectionSettings",
    "DataConnectorGongDiscriminatedConnectionSettingsSettings",
    "DataConnectorGoogleCalendarDiscriminatedConnectionSettings",
    "DataConnectorGoogleCalendarDiscriminatedConnectionSettingsSettings",
    "DataConnectorGoogleDocsDiscriminatedConnectionSettings",
    "DataConnectorGoogleDocsDiscriminatedConnectionSettingsSettings",
    "DataConnectorGoogleDriveDiscriminatedConnectionSettings",
    "DataConnectorGoogleDriveDiscriminatedConnectionSettingsSettings",
    "DataConnectorGoogleMailDiscriminatedConnectionSettings",
    "DataConnectorGoogleMailDiscriminatedConnectionSettingsSettings",
    "DataConnectorGoogleSheetDiscriminatedConnectionSettings",
    "DataConnectorGoogleSheetDiscriminatedConnectionSettingsSettings",
    "DataConnectorGorgiasDiscriminatedConnectionSettings",
    "DataConnectorGorgiasDiscriminatedConnectionSettingsSettings",
    "DataConnectorGrainDiscriminatedConnectionSettings",
    "DataConnectorGrainDiscriminatedConnectionSettingsSettings",
    "DataConnectorGumroadDiscriminatedConnectionSettings",
    "DataConnectorGumroadDiscriminatedConnectionSettingsSettings",
    "DataConnectorGustoDiscriminatedConnectionSettings",
    "DataConnectorGustoDiscriminatedConnectionSettingsSettings",
    "DataConnectorHarvestDiscriminatedConnectionSettings",
    "DataConnectorHarvestDiscriminatedConnectionSettingsSettings",
    "DataConnectorHighlevelDiscriminatedConnectionSettings",
    "DataConnectorHighlevelDiscriminatedConnectionSettingsSettings",
    "DataConnectorHubspotDiscriminatedConnectionSettings",
    "DataConnectorHubspotDiscriminatedConnectionSettingsSettings",
    "DataConnectorInstagramDiscriminatedConnectionSettings",
    "DataConnectorInstagramDiscriminatedConnectionSettingsSettings",
    "DataConnectorIntercomDiscriminatedConnectionSettings",
    "DataConnectorIntercomDiscriminatedConnectionSettingsSettings",
    "DataConnectorJiraDiscriminatedConnectionSettings",
    "DataConnectorJiraDiscriminatedConnectionSettingsSettings",
    "DataConnectorKeapDiscriminatedConnectionSettings",
    "DataConnectorKeapDiscriminatedConnectionSettingsSettings",
    "DataConnectorLeverDiscriminatedConnectionSettings",
    "DataConnectorLeverDiscriminatedConnectionSettingsSettings",
    "DataConnectorLinearDiscriminatedConnectionSettings",
    "DataConnectorLinearDiscriminatedConnectionSettingsSettings",
    "DataConnectorLinkedinDiscriminatedConnectionSettings",
    "DataConnectorLinkedinDiscriminatedConnectionSettingsSettings",
    "DataConnectorLinkhutDiscriminatedConnectionSettings",
    "DataConnectorLinkhutDiscriminatedConnectionSettingsSettings",
    "DataConnectorMailchimpDiscriminatedConnectionSettings",
    "DataConnectorMailchimpDiscriminatedConnectionSettingsSettings",
    "DataConnectorMiroDiscriminatedConnectionSettings",
    "DataConnectorMiroDiscriminatedConnectionSettingsSettings",
    "DataConnectorMondayDiscriminatedConnectionSettings",
    "DataConnectorMondayDiscriminatedConnectionSettingsSettings",
    "DataConnectorMuralDiscriminatedConnectionSettings",
    "DataConnectorMuralDiscriminatedConnectionSettingsSettings",
    "DataConnectorNamelyDiscriminatedConnectionSettings",
    "DataConnectorNamelyDiscriminatedConnectionSettingsSettings",
    "DataConnectorNationbuilderDiscriminatedConnectionSettings",
    "DataConnectorNationbuilderDiscriminatedConnectionSettingsSettings",
    "DataConnectorNetsuiteDiscriminatedConnectionSettings",
    "DataConnectorNetsuiteDiscriminatedConnectionSettingsSettings",
    "DataConnectorNotionDiscriminatedConnectionSettings",
    "DataConnectorNotionDiscriminatedConnectionSettingsSettings",
    "DataConnectorOdooDiscriminatedConnectionSettings",
    "DataConnectorOdooDiscriminatedConnectionSettingsSettings",
    "DataConnectorOktaDiscriminatedConnectionSettings",
    "DataConnectorOktaDiscriminatedConnectionSettingsSettings",
    "DataConnectorOsuDiscriminatedConnectionSettings",
    "DataConnectorOsuDiscriminatedConnectionSettingsSettings",
    "DataConnectorOuraDiscriminatedConnectionSettings",
    "DataConnectorOuraDiscriminatedConnectionSettingsSettings",
    "DataConnectorOutreachDiscriminatedConnectionSettings",
    "DataConnectorOutreachDiscriminatedConnectionSettingsSettings",
    "DataConnectorPagerdutyDiscriminatedConnectionSettings",
    "DataConnectorPagerdutyDiscriminatedConnectionSettingsSettings",
    "DataConnectorPandadocDiscriminatedConnectionSettings",
    "DataConnectorPandadocDiscriminatedConnectionSettingsSettings",
    "DataConnectorPayfitDiscriminatedConnectionSettings",
    "DataConnectorPayfitDiscriminatedConnectionSettingsSettings",
    "DataConnectorPaypalDiscriminatedConnectionSettings",
    "DataConnectorPaypalDiscriminatedConnectionSettingsSettings",
    "DataConnectorPennylaneDiscriminatedConnectionSettings",
    "DataConnectorPennylaneDiscriminatedConnectionSettingsSettings",
    "DataConnectorPinterestDiscriminatedConnectionSettings",
    "DataConnectorPinterestDiscriminatedConnectionSettingsSettings",
    "DataConnectorPipedriveDiscriminatedConnectionSettings",
    "DataConnectorPipedriveDiscriminatedConnectionSettingsSettings",
    "DataConnectorPodiumDiscriminatedConnectionSettings",
    "DataConnectorPodiumDiscriminatedConnectionSettingsSettings",
    "DataConnectorProductboardDiscriminatedConnectionSettings",
    "DataConnectorProductboardDiscriminatedConnectionSettingsSettings",
    "DataConnectorQualtricsDiscriminatedConnectionSettings",
    "DataConnectorQualtricsDiscriminatedConnectionSettingsSettings",
    "DataConnectorQuickbooksDiscriminatedConnectionSettings",
    "DataConnectorQuickbooksDiscriminatedConnectionSettingsSettings",
    "DataConnectorRedditDiscriminatedConnectionSettings",
    "DataConnectorRedditDiscriminatedConnectionSettingsSettings",
    "DataConnectorSageDiscriminatedConnectionSettings",
    "DataConnectorSageDiscriminatedConnectionSettingsSettings",
    "DataConnectorSalesforceDiscriminatedConnectionSettings",
    "DataConnectorSalesforceDiscriminatedConnectionSettingsSettings",
    "DataConnectorSalesloftDiscriminatedConnectionSettings",
    "DataConnectorSalesloftDiscriminatedConnectionSettingsSettings",
    "DataConnectorSegmentDiscriminatedConnectionSettings",
    "DataConnectorSegmentDiscriminatedConnectionSettingsSettings",
    "DataConnectorServicem8DiscriminatedConnectionSettings",
    "DataConnectorServicem8DiscriminatedConnectionSettingsSettings",
    "DataConnectorServicenowDiscriminatedConnectionSettings",
    "DataConnectorServicenowDiscriminatedConnectionSettingsSettings",
    "DataConnectorSharepointDiscriminatedConnectionSettings",
    "DataConnectorSharepointDiscriminatedConnectionSettingsSettings",
    "DataConnectorShopifyDiscriminatedConnectionSettings",
    "DataConnectorShopifyDiscriminatedConnectionSettingsSettings",
    "DataConnectorSignnowDiscriminatedConnectionSettings",
    "DataConnectorSignnowDiscriminatedConnectionSettingsSettings",
    "DataConnectorSlackDiscriminatedConnectionSettings",
    "DataConnectorSlackDiscriminatedConnectionSettingsSettings",
    "DataConnectorSmartsheetDiscriminatedConnectionSettings",
    "DataConnectorSmartsheetDiscriminatedConnectionSettingsSettings",
    "DataConnectorSnowflakeDiscriminatedConnectionSettings",
    "DataConnectorSnowflakeDiscriminatedConnectionSettingsSettings",
    "DataConnectorSpotifyDiscriminatedConnectionSettings",
    "DataConnectorSpotifyDiscriminatedConnectionSettingsSettings",
    "DataConnectorSquarespaceDiscriminatedConnectionSettings",
    "DataConnectorSquarespaceDiscriminatedConnectionSettingsSettings",
    "DataConnectorSquareupDiscriminatedConnectionSettings",
    "DataConnectorSquareupDiscriminatedConnectionSettingsSettings",
    "DataConnectorStackexchangeDiscriminatedConnectionSettings",
    "DataConnectorStackexchangeDiscriminatedConnectionSettingsSettings",
    "DataConnectorStravaDiscriminatedConnectionSettings",
    "DataConnectorStravaDiscriminatedConnectionSettingsSettings",
    "DataConnectorTeamworkDiscriminatedConnectionSettings",
    "DataConnectorTeamworkDiscriminatedConnectionSettingsSettings",
    "DataConnectorTicktickDiscriminatedConnectionSettings",
    "DataConnectorTicktickDiscriminatedConnectionSettingsSettings",
    "DataConnectorTimelyDiscriminatedConnectionSettings",
    "DataConnectorTimelyDiscriminatedConnectionSettingsSettings",
    "DataConnectorTodoistDiscriminatedConnectionSettings",
    "DataConnectorTodoistDiscriminatedConnectionSettingsSettings",
    "DataConnectorTremendousDiscriminatedConnectionSettings",
    "DataConnectorTremendousDiscriminatedConnectionSettingsSettings",
    "DataConnectorTsheetsteamDiscriminatedConnectionSettings",
    "DataConnectorTsheetsteamDiscriminatedConnectionSettingsSettings",
    "DataConnectorTumblrDiscriminatedConnectionSettings",
    "DataConnectorTumblrDiscriminatedConnectionSettingsSettings",
    "DataConnectorTwinfieldDiscriminatedConnectionSettings",
    "DataConnectorTwinfieldDiscriminatedConnectionSettingsSettings",
    "DataConnectorTwitchDiscriminatedConnectionSettings",
    "DataConnectorTwitchDiscriminatedConnectionSettingsSettings",
    "DataConnectorTwitterDiscriminatedConnectionSettings",
    "DataConnectorTwitterDiscriminatedConnectionSettingsSettings",
    "DataConnectorTypeformDiscriminatedConnectionSettings",
    "DataConnectorTypeformDiscriminatedConnectionSettingsSettings",
    "DataConnectorUberDiscriminatedConnectionSettings",
    "DataConnectorUberDiscriminatedConnectionSettingsSettings",
    "DataConnectorVimeoDiscriminatedConnectionSettings",
    "DataConnectorVimeoDiscriminatedConnectionSettingsSettings",
    "DataConnectorWakatimeDiscriminatedConnectionSettings",
    "DataConnectorWakatimeDiscriminatedConnectionSettingsSettings",
    "DataConnectorWealthboxDiscriminatedConnectionSettings",
    "DataConnectorWealthboxDiscriminatedConnectionSettingsSettings",
    "DataConnectorWebflowDiscriminatedConnectionSettings",
    "DataConnectorWebflowDiscriminatedConnectionSettingsSettings",
    "DataConnectorWhoopDiscriminatedConnectionSettings",
    "DataConnectorWhoopDiscriminatedConnectionSettingsSettings",
    "DataConnectorWordpressDiscriminatedConnectionSettings",
    "DataConnectorWordpressDiscriminatedConnectionSettingsSettings",
    "DataConnectorWrikeDiscriminatedConnectionSettings",
    "DataConnectorWrikeDiscriminatedConnectionSettingsSettings",
    "DataConnectorXeroDiscriminatedConnectionSettings",
    "DataConnectorXeroDiscriminatedConnectionSettingsSettings",
    "DataConnectorYahooDiscriminatedConnectionSettings",
    "DataConnectorYahooDiscriminatedConnectionSettingsSettings",
    "DataConnectorYandexDiscriminatedConnectionSettings",
    "DataConnectorYandexDiscriminatedConnectionSettingsSettings",
    "DataConnectorZapierDiscriminatedConnectionSettings",
    "DataConnectorZapierDiscriminatedConnectionSettingsSettings",
    "DataConnectorZendeskDiscriminatedConnectionSettings",
    "DataConnectorZendeskDiscriminatedConnectionSettingsSettings",
    "DataConnectorZenefitsDiscriminatedConnectionSettings",
    "DataConnectorZenefitsDiscriminatedConnectionSettingsSettings",
    "DataConnectorZohoDeskDiscriminatedConnectionSettings",
    "DataConnectorZohoDeskDiscriminatedConnectionSettingsSettings",
    "DataConnectorZohoDiscriminatedConnectionSettings",
    "DataConnectorZohoDiscriminatedConnectionSettingsSettings",
    "DataConnectorZoomDiscriminatedConnectionSettings",
    "DataConnectorZoomDiscriminatedConnectionSettingsSettings",
    "DataConnectorAirtableDiscriminatedConnectionSettings",
    "DataConnectorAirtableDiscriminatedConnectionSettingsSettings",
    "DataConnectorApolloDiscriminatedConnectionSettings",
    "DataConnectorApolloDiscriminatedConnectionSettingsSettings",
    "DataConnectorBrexDiscriminatedConnectionSettings",
    "DataConnectorBrexDiscriminatedConnectionSettingsSettings",
    "DataConnectorCodaDiscriminatedConnectionSettings",
    "DataConnectorCodaDiscriminatedConnectionSettingsSettings",
    "DataConnectorFinchDiscriminatedConnectionSettings",
    "DataConnectorFinchDiscriminatedConnectionSettingsSettings",
    "DataConnectorFirebaseDiscriminatedConnectionSettings",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettings",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0ServiceAccount",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthData",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJson",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember1",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember2",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1FirebaseConfig",
    "DataConnectorForeceiptDiscriminatedConnectionSettings",
    "DataConnectorForeceiptDiscriminatedConnectionSettingsSettings",
    "DataConnectorGreenhouseDiscriminatedConnectionSettings",
    "DataConnectorGreenhouseDiscriminatedConnectionSettingsSettings",
    "DataConnectorHeronDiscriminatedConnectionSettings",
    "DataConnectorLunchmoneyDiscriminatedConnectionSettings",
    "DataConnectorMercuryDiscriminatedConnectionSettings",
    "DataConnectorMergeDiscriminatedConnectionSettings",
    "DataConnectorMergeDiscriminatedConnectionSettingsSettings",
    "DataConnectorMootaDiscriminatedConnectionSettings",
    "DataConnectorOnebrickDiscriminatedConnectionSettings",
    "DataConnectorOnebrickDiscriminatedConnectionSettingsSettings",
    "DataConnectorOpenledgerDiscriminatedConnectionSettings",
    "DataConnectorOpenledgerDiscriminatedConnectionSettingsSettings",
    "DataConnectorPlaidDiscriminatedConnectionSettings",
    "DataConnectorPlaidDiscriminatedConnectionSettingsSettings",
    "DataConnectorPostgresDiscriminatedConnectionSettings",
    "DataConnectorPostgresDiscriminatedConnectionSettingsSettings",
    "DataConnectorRampDiscriminatedConnectionSettings",
    "DataConnectorRampDiscriminatedConnectionSettingsSettings",
    "DataConnectorSaltedgeDiscriminatedConnectionSettings",
    "DataConnectorSplitwiseDiscriminatedConnectionSettings",
    "DataConnectorSplitwiseDiscriminatedConnectionSettingsSettings",
    "DataConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUser",
    "DataConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserNotifications",
    "DataConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserPicture",
    "DataConnectorStripeDiscriminatedConnectionSettings",
    "DataConnectorStripeDiscriminatedConnectionSettingsSettings",
    "DataConnectorTellerDiscriminatedConnectionSettings",
    "DataConnectorTellerDiscriminatedConnectionSettingsSettings",
    "DataConnectorTogglDiscriminatedConnectionSettings",
    "DataConnectorTogglDiscriminatedConnectionSettingsSettings",
    "DataConnectorTwentyDiscriminatedConnectionSettings",
    "DataConnectorTwentyDiscriminatedConnectionSettingsSettings",
    "DataConnectorVenmoDiscriminatedConnectionSettings",
    "DataConnectorVenmoDiscriminatedConnectionSettingsSettings",
    "DataConnectorWiseDiscriminatedConnectionSettings",
    "DataConnectorWiseDiscriminatedConnectionSettingsSettings",
    "DataConnectorYodleeDiscriminatedConnectionSettings",
    "DataConnectorYodleeDiscriminatedConnectionSettingsSettings",
    "DataConnectorYodleeDiscriminatedConnectionSettingsSettingsAccessToken",
    "DataConnectorYodleeDiscriminatedConnectionSettingsSettingsProviderAccount",
]


class ClientCreateConnectionParams(TypedDict, total=False):
    connector_config_id: Required[str]
    """The id of the connector config, starts with `ccfg_`"""

    customer_id: Required[str]
    """The id of the customer in your application.

    Ensure it is unique for that customer.
    """

    data: Required[Data]
    """Connector specific data"""

    check_connection: bool
    """Perform a synchronous connection check before creating it."""

    metadata: Dict[str, object]


class DataConnectorAcceloDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    subdomain: Required[str]
    """The subdomain of your Accelo account (e.g., https://domain.api.accelo.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAcceloDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["accelo"]]

    settings: DataConnectorAcceloDiscriminatedConnectionSettingsSettings


class DataConnectorAcmeOauth2DiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAcmeOauth2DiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["acme-oauth2"]]

    settings: DataConnectorAcmeOauth2DiscriminatedConnectionSettingsSettings


class DataConnectorAdobeDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAdobeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["adobe"]]

    settings: DataConnectorAdobeDiscriminatedConnectionSettingsSettings


class DataConnectorAdyenDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    environment: Required[str]
    """The environment to use (e.g., live|test)"""

    oauth: Required[OAuthConnectionSettingsParam]

    resource: Required[str]
    """
    The resource to use for your various requests (e.g.,
    https://kyc-(live|test).adyen.com)
    """

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAdyenDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["adyen"]]

    settings: DataConnectorAdyenDiscriminatedConnectionSettingsSettings


class DataConnectorAircallDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAircallDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["aircall"]]

    settings: DataConnectorAircallDiscriminatedConnectionSettingsSettings


class DataConnectorAmazonDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    extension: Required[str]
    """The domain extension for your Amazon account (e.g., com)"""

    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAmazonDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["amazon"]]

    settings: DataConnectorAmazonDiscriminatedConnectionSettingsSettings


class DataConnectorApaleoDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorApaleoDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["apaleo"]]

    settings: DataConnectorApaleoDiscriminatedConnectionSettingsSettings


class DataConnectorAsanaDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAsanaDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["asana"]]

    settings: DataConnectorAsanaDiscriminatedConnectionSettingsSettings


class DataConnectorAttioDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAttioDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["attio"]]

    settings: DataConnectorAttioDiscriminatedConnectionSettingsSettings


class DataConnectorAuth0DiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    subdomain: Required[str]
    """The subdomain of your Auth0 account (e.g., https://domain.auth0.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAuth0DiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["auth0"]]

    settings: DataConnectorAuth0DiscriminatedConnectionSettingsSettings


class DataConnectorAutodeskDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAutodeskDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["autodesk"]]

    settings: DataConnectorAutodeskDiscriminatedConnectionSettingsSettings


class DataConnectorAwsDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_subdomain: Required[Annotated[str, PropertyInfo(alias="apiSubdomain")]]
    """
    The API subdomain to the API you want to connect to (e.g.,
    https://cognito-idp.us-east-2.amazonaws.com)
    """

    extension: Required[str]
    """The domain extension of your AWS account (e.g., com)"""

    oauth: Required[OAuthConnectionSettingsParam]

    subdomain: Required[str]
    """The subdomain of your AWS account (e.g., https://domain.amazoncognito.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAwsDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["aws"]]

    settings: DataConnectorAwsDiscriminatedConnectionSettingsSettings


class DataConnectorBamboohrDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    subdomain: Required[str]
    """The subdomain of your BambooHR account (e.g., https://domain.bamboohr.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBamboohrDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["bamboohr"]]

    settings: DataConnectorBamboohrDiscriminatedConnectionSettingsSettings


class DataConnectorBasecampDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    account_id: Required[Annotated[str, PropertyInfo(alias="accountId")]]
    """Your Account ID (e.g., 5899981)"""

    app_details: Required[Annotated[str, PropertyInfo(alias="appDetails")]]
    """The details of your app (e.g., example-subdomain)"""

    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBasecampDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["basecamp"]]

    settings: DataConnectorBasecampDiscriminatedConnectionSettingsSettings


class DataConnectorBattlenetDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_domain: Required[Annotated[str, PropertyInfo(alias="apiDomain")]]
    """
    The domain to where you will access your API (e.g., https://us.api.blizzard.com)
    """

    extension: Required[str]
    """The domain extension of your Battle.net account (e.g., com)"""

    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBattlenetDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["battlenet"]]

    settings: DataConnectorBattlenetDiscriminatedConnectionSettingsSettings


class DataConnectorBigcommerceDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    account_uuid: Required[Annotated[str, PropertyInfo(alias="accountUuid")]]
    """
    The account UUID of your BigCommerce account (e.g.,
    123e4567-e89b-12d3-a456-426614174000)
    """

    oauth: Required[OAuthConnectionSettingsParam]

    store_hash: Required[Annotated[str, PropertyInfo(alias="storeHash")]]
    """The store hash of your BigCommerce account (e.g., Example123)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBigcommerceDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["bigcommerce"]]

    settings: DataConnectorBigcommerceDiscriminatedConnectionSettingsSettings


class DataConnectorBitbucketDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBitbucketDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["bitbucket"]]

    settings: DataConnectorBitbucketDiscriminatedConnectionSettingsSettings


class DataConnectorBitlyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBitlyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["bitly"]]

    settings: DataConnectorBitlyDiscriminatedConnectionSettingsSettings


class DataConnectorBlackbaudDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBlackbaudDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["blackbaud"]]

    settings: DataConnectorBlackbaudDiscriminatedConnectionSettingsSettings


class DataConnectorBoldsignDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBoldsignDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["boldsign"]]

    settings: DataConnectorBoldsignDiscriminatedConnectionSettingsSettings


class DataConnectorBoxDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBoxDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["box"]]

    settings: DataConnectorBoxDiscriminatedConnectionSettingsSettings


class DataConnectorBraintreeDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBraintreeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["braintree"]]

    settings: DataConnectorBraintreeDiscriminatedConnectionSettingsSettings


class DataConnectorCalendlyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorCalendlyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["calendly"]]

    settings: DataConnectorCalendlyDiscriminatedConnectionSettingsSettings


class DataConnectorClickupDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorClickupDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["clickup"]]

    settings: DataConnectorClickupDiscriminatedConnectionSettingsSettings


class DataConnectorCloseDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorCloseDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["close"]]

    settings: DataConnectorCloseDiscriminatedConnectionSettingsSettings


class DataConnectorConfluenceDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorConfluenceDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["confluence"]]

    settings: DataConnectorConfluenceDiscriminatedConnectionSettingsSettings


class DataConnectorContentfulDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    subdomain: Required[str]
    """The subdomain of your Contentful account (e.g., https://domain.contentful.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorContentfulDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["contentful"]]

    settings: DataConnectorContentfulDiscriminatedConnectionSettingsSettings


class DataConnectorContentstackDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_domain: Required[Annotated[str, PropertyInfo(alias="apiDomain")]]
    """
    The domain to where you will access your API (e.g.,
    https://eu-api.contentstack.com)
    """

    app_id: Required[Annotated[str, PropertyInfo(alias="appId")]]
    """The app ID of your Contentstack account (e.g., example-subdomain)"""

    oauth: Required[OAuthConnectionSettingsParam]

    subdomain: Required[str]
    """
    The subdomain of your Contentstack account (e.g.,
    https://domain.contentstack.com)
    """

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorContentstackDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["contentstack"]]

    settings: DataConnectorContentstackDiscriminatedConnectionSettingsSettings


class DataConnectorCopperDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorCopperDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["copper"]]

    settings: DataConnectorCopperDiscriminatedConnectionSettingsSettings


class DataConnectorCorosDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorCorosDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["coros"]]

    settings: DataConnectorCorosDiscriminatedConnectionSettingsSettings


class DataConnectorDatevDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorDatevDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["datev"]]

    settings: DataConnectorDatevDiscriminatedConnectionSettingsSettings


class DataConnectorDeelDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorDeelDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["deel"]]

    settings: DataConnectorDeelDiscriminatedConnectionSettingsSettings


class DataConnectorDialpadDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorDialpadDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["dialpad"]]

    settings: DataConnectorDialpadDiscriminatedConnectionSettingsSettings


class DataConnectorDigitaloceanDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorDigitaloceanDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["digitalocean"]]

    settings: DataConnectorDigitaloceanDiscriminatedConnectionSettingsSettings


class DataConnectorDiscordDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorDiscordDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["discord"]]

    settings: DataConnectorDiscordDiscriminatedConnectionSettingsSettings


class DataConnectorDocusignDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorDocusignDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["docusign"]]

    settings: DataConnectorDocusignDiscriminatedConnectionSettingsSettings


class DataConnectorDropboxDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorDropboxDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["dropbox"]]

    settings: DataConnectorDropboxDiscriminatedConnectionSettingsSettings


class DataConnectorEbayDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorEbayDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["ebay"]]

    settings: DataConnectorEbayDiscriminatedConnectionSettingsSettings


class DataConnectorEgnyteDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    subdomain: Required[str]
    """The subdomain of your Egnyte account (e.g., https://domain.egnyte.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorEgnyteDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["egnyte"]]

    settings: DataConnectorEgnyteDiscriminatedConnectionSettingsSettings


class DataConnectorEnvoyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorEnvoyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["envoy"]]

    settings: DataConnectorEnvoyDiscriminatedConnectionSettingsSettings


class DataConnectorEventbriteDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorEventbriteDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["eventbrite"]]

    settings: DataConnectorEventbriteDiscriminatedConnectionSettingsSettings


class DataConnectorExistDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorExistDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["exist"]]

    settings: DataConnectorExistDiscriminatedConnectionSettingsSettings


class DataConnectorFacebookDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorFacebookDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["facebook"]]

    settings: DataConnectorFacebookDiscriminatedConnectionSettingsSettings


class DataConnectorFactorialDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorFactorialDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["factorial"]]

    settings: DataConnectorFactorialDiscriminatedConnectionSettingsSettings


class DataConnectorFigmaDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorFigmaDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["figma"]]

    settings: DataConnectorFigmaDiscriminatedConnectionSettingsSettings


class DataConnectorFitbitDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorFitbitDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["fitbit"]]

    settings: DataConnectorFitbitDiscriminatedConnectionSettingsSettings


class DataConnectorFortnoxDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorFortnoxDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["fortnox"]]

    settings: DataConnectorFortnoxDiscriminatedConnectionSettingsSettings


class DataConnectorFreshbooksDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorFreshbooksDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["freshbooks"]]

    settings: DataConnectorFreshbooksDiscriminatedConnectionSettingsSettings


class DataConnectorFrontDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorFrontDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["front"]]

    settings: DataConnectorFrontDiscriminatedConnectionSettingsSettings


class DataConnectorGitHubDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGitHubDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["github"]]

    settings: DataConnectorGitHubDiscriminatedConnectionSettingsSettings


class DataConnectorGitlabDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGitlabDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["gitlab"]]

    settings: DataConnectorGitlabDiscriminatedConnectionSettingsSettings


class DataConnectorGongDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_base_url_for_customer: Required[str]
    """The base URL of your Gong account (e.g., example)"""

    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGongDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["gong"]]

    settings: DataConnectorGongDiscriminatedConnectionSettingsSettings


class DataConnectorGoogleCalendarDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGoogleCalendarDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["google-calendar"]]

    settings: DataConnectorGoogleCalendarDiscriminatedConnectionSettingsSettings


class DataConnectorGoogleDocsDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGoogleDocsDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["google-docs"]]

    settings: DataConnectorGoogleDocsDiscriminatedConnectionSettingsSettings


class DataConnectorGoogleDriveDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGoogleDriveDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["google-drive"]]

    settings: DataConnectorGoogleDriveDiscriminatedConnectionSettingsSettings


class DataConnectorGoogleMailDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGoogleMailDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["google-mail"]]

    settings: DataConnectorGoogleMailDiscriminatedConnectionSettingsSettings


class DataConnectorGoogleSheetDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGoogleSheetDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["google-sheet"]]

    settings: DataConnectorGoogleSheetDiscriminatedConnectionSettingsSettings


class DataConnectorGorgiasDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    subdomain: Required[str]
    """The subdomain of your Gorgias account (e.g., https://domain.gorgias.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGorgiasDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["gorgias"]]

    settings: DataConnectorGorgiasDiscriminatedConnectionSettingsSettings


class DataConnectorGrainDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGrainDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["grain"]]

    settings: DataConnectorGrainDiscriminatedConnectionSettingsSettings


class DataConnectorGumroadDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGumroadDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["gumroad"]]

    settings: DataConnectorGumroadDiscriminatedConnectionSettingsSettings


class DataConnectorGustoDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGustoDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["gusto"]]

    settings: DataConnectorGustoDiscriminatedConnectionSettingsSettings


class DataConnectorHarvestDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    app_details: Required[Annotated[str, PropertyInfo(alias="appDetails")]]
    """The details of your app (e.g., example-subdomain)"""

    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorHarvestDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["harvest"]]

    settings: DataConnectorHarvestDiscriminatedConnectionSettingsSettings


class DataConnectorHighlevelDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorHighlevelDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["highlevel"]]

    settings: DataConnectorHighlevelDiscriminatedConnectionSettingsSettings


class DataConnectorHubspotDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorHubspotDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["hubspot"]]

    settings: DataConnectorHubspotDiscriminatedConnectionSettingsSettings


class DataConnectorInstagramDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorInstagramDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["instagram"]]

    settings: DataConnectorInstagramDiscriminatedConnectionSettingsSettings


class DataConnectorIntercomDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorIntercomDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["intercom"]]

    settings: DataConnectorIntercomDiscriminatedConnectionSettingsSettings


class DataConnectorJiraDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorJiraDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["jira"]]

    settings: DataConnectorJiraDiscriminatedConnectionSettingsSettings


class DataConnectorKeapDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorKeapDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["keap"]]

    settings: DataConnectorKeapDiscriminatedConnectionSettingsSettings


class DataConnectorLeverDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorLeverDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["lever"]]

    settings: DataConnectorLeverDiscriminatedConnectionSettingsSettings


class DataConnectorLinearDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorLinearDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["linear"]]

    settings: DataConnectorLinearDiscriminatedConnectionSettingsSettings


class DataConnectorLinkedinDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorLinkedinDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["linkedin"]]

    settings: DataConnectorLinkedinDiscriminatedConnectionSettingsSettings


class DataConnectorLinkhutDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorLinkhutDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["linkhut"]]

    settings: DataConnectorLinkhutDiscriminatedConnectionSettingsSettings


class DataConnectorMailchimpDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    dc: Required[str]
    """The data center for your account (e.g., us6)"""

    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorMailchimpDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["mailchimp"]]

    settings: DataConnectorMailchimpDiscriminatedConnectionSettingsSettings


class DataConnectorMiroDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorMiroDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["miro"]]

    settings: DataConnectorMiroDiscriminatedConnectionSettingsSettings


class DataConnectorMondayDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorMondayDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["monday"]]

    settings: DataConnectorMondayDiscriminatedConnectionSettingsSettings


class DataConnectorMuralDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorMuralDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["mural"]]

    settings: DataConnectorMuralDiscriminatedConnectionSettingsSettings


class DataConnectorNamelyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    company: Required[str]
    """The name of your Namely company (e.g., example)"""

    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorNamelyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["namely"]]

    settings: DataConnectorNamelyDiscriminatedConnectionSettingsSettings


class DataConnectorNationbuilderDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    account_id: Required[Annotated[str, PropertyInfo(alias="accountId")]]
    """The account ID of your NationBuilder account (e.g., example-subdomain)"""

    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorNationbuilderDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["nationbuilder"]]

    settings: DataConnectorNationbuilderDiscriminatedConnectionSettingsSettings


class DataConnectorNetsuiteDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    account_id: Required[Annotated[str, PropertyInfo(alias="accountId")]]
    """The account ID of your NetSuite account (e.g., tstdrv231585)"""

    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorNetsuiteDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["netsuite"]]

    settings: DataConnectorNetsuiteDiscriminatedConnectionSettingsSettings


class DataConnectorNotionDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorNotionDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["notion"]]

    settings: DataConnectorNotionDiscriminatedConnectionSettingsSettings


class DataConnectorOdooDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    server_url: Required[Annotated[str, PropertyInfo(alias="serverUrl")]]
    """The domain of your Odoo account (e.g., https://example-subdomain)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorOdooDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["odoo"]]

    settings: DataConnectorOdooDiscriminatedConnectionSettingsSettings


class DataConnectorOktaDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    subdomain: Required[str]
    """The subdomain of your Okta account (e.g., https://domain.okta.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorOktaDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["okta"]]

    settings: DataConnectorOktaDiscriminatedConnectionSettingsSettings


class DataConnectorOsuDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorOsuDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["osu"]]

    settings: DataConnectorOsuDiscriminatedConnectionSettingsSettings


class DataConnectorOuraDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorOuraDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["oura"]]

    settings: DataConnectorOuraDiscriminatedConnectionSettingsSettings


class DataConnectorOutreachDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorOutreachDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["outreach"]]

    settings: DataConnectorOutreachDiscriminatedConnectionSettingsSettings


class DataConnectorPagerdutyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorPagerdutyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["pagerduty"]]

    settings: DataConnectorPagerdutyDiscriminatedConnectionSettingsSettings


class DataConnectorPandadocDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorPandadocDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["pandadoc"]]

    settings: DataConnectorPandadocDiscriminatedConnectionSettingsSettings


class DataConnectorPayfitDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorPayfitDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["payfit"]]

    settings: DataConnectorPayfitDiscriminatedConnectionSettingsSettings


class DataConnectorPaypalDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorPaypalDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["paypal"]]

    settings: DataConnectorPaypalDiscriminatedConnectionSettingsSettings


class DataConnectorPennylaneDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorPennylaneDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["pennylane"]]

    settings: DataConnectorPennylaneDiscriminatedConnectionSettingsSettings


class DataConnectorPinterestDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorPinterestDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["pinterest"]]

    settings: DataConnectorPinterestDiscriminatedConnectionSettingsSettings


class DataConnectorPipedriveDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_domain: Required[str]
    """The API URL of your Pipedrive account (e.g., example)"""

    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorPipedriveDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["pipedrive"]]

    settings: DataConnectorPipedriveDiscriminatedConnectionSettingsSettings


class DataConnectorPodiumDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The API version of your Podium account (e.g., example-subdomain)"""

    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorPodiumDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["podium"]]

    settings: DataConnectorPodiumDiscriminatedConnectionSettingsSettings


class DataConnectorProductboardDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorProductboardDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["productboard"]]

    settings: DataConnectorProductboardDiscriminatedConnectionSettingsSettings


class DataConnectorQualtricsDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    subdomain: Required[str]
    """The subdomain of your Qualtrics account (e.g., https://domain.qualtrics.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorQualtricsDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["qualtrics"]]

    settings: DataConnectorQualtricsDiscriminatedConnectionSettingsSettings


class DataConnectorQuickbooksDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorQuickbooksDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["quickbooks"]]

    settings: DataConnectorQuickbooksDiscriminatedConnectionSettingsSettings


class DataConnectorRedditDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorRedditDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["reddit"]]

    settings: DataConnectorRedditDiscriminatedConnectionSettingsSettings


class DataConnectorSageDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSageDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["sage"]]

    settings: DataConnectorSageDiscriminatedConnectionSettingsSettings


class DataConnectorSalesforceDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    instance_url: Required[str]
    """The instance URL of your Salesforce account (e.g., example)"""

    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSalesforceDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["salesforce"]]

    settings: DataConnectorSalesforceDiscriminatedConnectionSettingsSettings


class DataConnectorSalesloftDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSalesloftDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["salesloft"]]

    settings: DataConnectorSalesloftDiscriminatedConnectionSettingsSettings


class DataConnectorSegmentDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSegmentDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["segment"]]

    settings: DataConnectorSegmentDiscriminatedConnectionSettingsSettings


class DataConnectorServicem8DiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorServicem8DiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["servicem8"]]

    settings: DataConnectorServicem8DiscriminatedConnectionSettingsSettings


class DataConnectorServicenowDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    subdomain: Required[str]
    """The subdomain of your ServiceNow account (e.g., https://domain.service-now.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorServicenowDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["servicenow"]]

    settings: DataConnectorServicenowDiscriminatedConnectionSettingsSettings


class DataConnectorSharepointDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSharepointDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["sharepoint"]]

    settings: DataConnectorSharepointDiscriminatedConnectionSettingsSettings


class DataConnectorShopifyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    subdomain: Required[str]
    """The subdomain of your Shopify account (e.g., https://domain.myshopify.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorShopifyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["shopify"]]

    settings: DataConnectorShopifyDiscriminatedConnectionSettingsSettings


class DataConnectorSignnowDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSignnowDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["signnow"]]

    settings: DataConnectorSignnowDiscriminatedConnectionSettingsSettings


class DataConnectorSlackDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSlackDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["slack"]]

    settings: DataConnectorSlackDiscriminatedConnectionSettingsSettings


class DataConnectorSmartsheetDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSmartsheetDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["smartsheet"]]

    settings: DataConnectorSmartsheetDiscriminatedConnectionSettingsSettings


class DataConnectorSnowflakeDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    snowflake_account_url: Required[str]
    """The domain of your Snowflake account (e.g., https://example-subdomain)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSnowflakeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["snowflake"]]

    settings: DataConnectorSnowflakeDiscriminatedConnectionSettingsSettings


class DataConnectorSpotifyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSpotifyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["spotify"]]

    settings: DataConnectorSpotifyDiscriminatedConnectionSettingsSettings


class DataConnectorSquarespaceDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    customapp_description: Required[Annotated[str, PropertyInfo(alias="customappDescription")]]
    """The user agent of your custom app (e.g., example-subdomain)"""

    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSquarespaceDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["squarespace"]]

    settings: DataConnectorSquarespaceDiscriminatedConnectionSettingsSettings


class DataConnectorSquareupDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSquareupDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["squareup"]]

    settings: DataConnectorSquareupDiscriminatedConnectionSettingsSettings


class DataConnectorStackexchangeDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorStackexchangeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["stackexchange"]]

    settings: DataConnectorStackexchangeDiscriminatedConnectionSettingsSettings


class DataConnectorStravaDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorStravaDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["strava"]]

    settings: DataConnectorStravaDiscriminatedConnectionSettingsSettings


class DataConnectorTeamworkDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTeamworkDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["teamwork"]]

    settings: DataConnectorTeamworkDiscriminatedConnectionSettingsSettings


class DataConnectorTicktickDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTicktickDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["ticktick"]]

    settings: DataConnectorTicktickDiscriminatedConnectionSettingsSettings


class DataConnectorTimelyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTimelyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["timely"]]

    settings: DataConnectorTimelyDiscriminatedConnectionSettingsSettings


class DataConnectorTodoistDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTodoistDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["todoist"]]

    settings: DataConnectorTodoistDiscriminatedConnectionSettingsSettings


class DataConnectorTremendousDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTremendousDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["tremendous"]]

    settings: DataConnectorTremendousDiscriminatedConnectionSettingsSettings


class DataConnectorTsheetsteamDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTsheetsteamDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["tsheetsteam"]]

    settings: DataConnectorTsheetsteamDiscriminatedConnectionSettingsSettings


class DataConnectorTumblrDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTumblrDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["tumblr"]]

    settings: DataConnectorTumblrDiscriminatedConnectionSettingsSettings


class DataConnectorTwinfieldDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    cluster: Required[str]
    """The cluster to your Twinfield instance (e.g., https://accounting.twinfield.com)"""

    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTwinfieldDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["twinfield"]]

    settings: DataConnectorTwinfieldDiscriminatedConnectionSettingsSettings


class DataConnectorTwitchDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTwitchDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["twitch"]]

    settings: DataConnectorTwitchDiscriminatedConnectionSettingsSettings


class DataConnectorTwitterDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTwitterDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["twitter"]]

    settings: DataConnectorTwitterDiscriminatedConnectionSettingsSettings


class DataConnectorTypeformDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTypeformDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["typeform"]]

    settings: DataConnectorTypeformDiscriminatedConnectionSettingsSettings


class DataConnectorUberDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorUberDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["uber"]]

    settings: DataConnectorUberDiscriminatedConnectionSettingsSettings


class DataConnectorVimeoDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorVimeoDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["vimeo"]]

    settings: DataConnectorVimeoDiscriminatedConnectionSettingsSettings


class DataConnectorWakatimeDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorWakatimeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["wakatime"]]

    settings: DataConnectorWakatimeDiscriminatedConnectionSettingsSettings


class DataConnectorWealthboxDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorWealthboxDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["wealthbox"]]

    settings: DataConnectorWealthboxDiscriminatedConnectionSettingsSettings


class DataConnectorWebflowDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorWebflowDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["webflow"]]

    settings: DataConnectorWebflowDiscriminatedConnectionSettingsSettings


class DataConnectorWhoopDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorWhoopDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["whoop"]]

    settings: DataConnectorWhoopDiscriminatedConnectionSettingsSettings


class DataConnectorWordpressDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorWordpressDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["wordpress"]]

    settings: DataConnectorWordpressDiscriminatedConnectionSettingsSettings


class DataConnectorWrikeDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    host: Required[str]
    """The domain of your Wrike account (e.g., https://example-subdomain)"""

    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorWrikeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["wrike"]]

    settings: DataConnectorWrikeDiscriminatedConnectionSettingsSettings


class DataConnectorXeroDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorXeroDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["xero"]]

    settings: DataConnectorXeroDiscriminatedConnectionSettingsSettings


class DataConnectorYahooDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_domain: Required[Annotated[str, PropertyInfo(alias="apiDomain")]]
    """
    The domain to the API you want to connect to (e.g.,
    https://fantasysports.yahooapis.com)
    """

    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorYahooDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["yahoo"]]

    settings: DataConnectorYahooDiscriminatedConnectionSettingsSettings


class DataConnectorYandexDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorYandexDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["yandex"]]

    settings: DataConnectorYandexDiscriminatedConnectionSettingsSettings


class DataConnectorZapierDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorZapierDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["zapier"]]

    settings: DataConnectorZapierDiscriminatedConnectionSettingsSettings


class DataConnectorZendeskDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    subdomain: Required[str]
    """The subdomain of your Zendesk account (e.g., https://domain.zendesk.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorZendeskDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["zendesk"]]

    settings: DataConnectorZendeskDiscriminatedConnectionSettingsSettings


class DataConnectorZenefitsDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorZenefitsDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["zenefits"]]

    settings: DataConnectorZenefitsDiscriminatedConnectionSettingsSettings


class DataConnectorZohoDeskDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    extension: Required[str]
    """The domain extension of your Zoho account (e.g., https://accounts.zoho.com/)"""

    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorZohoDeskDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["zoho-desk"]]

    settings: DataConnectorZohoDeskDiscriminatedConnectionSettingsSettings


class DataConnectorZohoDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    extension: Required[str]
    """The domain extension of your Zoho account (e.g., https://accounts.zoho.com/)"""

    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorZohoDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["zoho"]]

    settings: DataConnectorZohoDiscriminatedConnectionSettingsSettings


class DataConnectorZoomDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[OAuthConnectionSettingsParam]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorZoomDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["zoom"]]

    settings: DataConnectorZoomDiscriminatedConnectionSettingsSettings


class DataConnectorAirtableDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    airtable_base: Required[Annotated[str, PropertyInfo(alias="airtableBase")]]

    api_key: Required[Annotated[str, PropertyInfo(alias="apiKey")]]


class DataConnectorAirtableDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["airtable"]]

    settings: DataConnectorAirtableDiscriminatedConnectionSettingsSettings


class DataConnectorApolloDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_key: Required[str]


class DataConnectorApolloDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["apollo"]]

    settings: DataConnectorApolloDiscriminatedConnectionSettingsSettings


class DataConnectorBrexDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    access_token: Required[Annotated[str, PropertyInfo(alias="accessToken")]]


class DataConnectorBrexDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["brex"]]

    settings: DataConnectorBrexDiscriminatedConnectionSettingsSettings


class DataConnectorCodaDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_key: Required[Annotated[str, PropertyInfo(alias="apiKey")]]


class DataConnectorCodaDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["coda"]]

    settings: DataConnectorCodaDiscriminatedConnectionSettingsSettings


class DataConnectorFinchDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    access_token: Required[str]


class DataConnectorFinchDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["finch"]]

    settings: DataConnectorFinchDiscriminatedConnectionSettingsSettings


class DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0ServiceAccountTyped(
    TypedDict, total=False
):
    project_id: Required[str]


DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0ServiceAccount: TypeAlias = Union[
    DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0ServiceAccountTyped, Dict[str, object]
]


class DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0(TypedDict, total=False):
    role: Required[Literal["admin"]]

    service_account: Required[
        Annotated[
            DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0ServiceAccount,
            PropertyInfo(alias="serviceAccount"),
        ]
    ]


class DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJsonTyped(
    TypedDict, total=False
):
    app_name: Required[Annotated[str, PropertyInfo(alias="appName")]]

    sts_token_manager: Required[Annotated[Dict[str, object], PropertyInfo(alias="stsTokenManager")]]

    uid: Required[str]


DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJson: TypeAlias = Union[
    DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJsonTyped,
    Dict[str, object],
]


class DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0(
    TypedDict, total=False
):
    method: Required[Literal["userJson"]]

    user_json: Required[
        Annotated[
            DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJson,
            PropertyInfo(alias="userJson"),
        ]
    ]


class DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember1(
    TypedDict, total=False
):
    custom_token: Required[Annotated[str, PropertyInfo(alias="customToken")]]

    method: Required[Literal["customToken"]]


class DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember2(
    TypedDict, total=False
):
    email: Required[str]

    method: Required[Literal["emailPassword"]]

    password: Required[str]


DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthData: TypeAlias = Union[
    DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0,
    DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember1,
    DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember2,
]


class DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1FirebaseConfig(TypedDict, total=False):
    api_key: Required[Annotated[str, PropertyInfo(alias="apiKey")]]

    app_id: Required[Annotated[str, PropertyInfo(alias="appId")]]

    auth_domain: Required[Annotated[str, PropertyInfo(alias="authDomain")]]

    database_url: Required[Annotated[str, PropertyInfo(alias="databaseURL")]]

    project_id: Required[Annotated[str, PropertyInfo(alias="projectId")]]

    measurement_id: Annotated[str, PropertyInfo(alias="measurementId")]

    messaging_sender_id: Annotated[str, PropertyInfo(alias="messagingSenderId")]

    storage_bucket: Annotated[str, PropertyInfo(alias="storageBucket")]


class DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1(TypedDict, total=False):
    auth_data: Required[
        Annotated[
            DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthData,
            PropertyInfo(alias="authData"),
        ]
    ]

    firebase_config: Required[
        Annotated[
            DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1FirebaseConfig,
            PropertyInfo(alias="firebaseConfig"),
        ]
    ]

    role: Required[Literal["user"]]


DataConnectorFirebaseDiscriminatedConnectionSettingsSettings: TypeAlias = Union[
    DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0,
    DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1,
]


class DataConnectorFirebaseDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["firebase"]]

    settings: DataConnectorFirebaseDiscriminatedConnectionSettingsSettings


class DataConnectorForeceiptDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    env_name: Required[Annotated[Literal["staging", "production"], PropertyInfo(alias="envName")]]

    _id: object

    credentials: object


class DataConnectorForeceiptDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["foreceipt"]]

    settings: DataConnectorForeceiptDiscriminatedConnectionSettingsSettings


class DataConnectorGreenhouseDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_key: Required[Annotated[str, PropertyInfo(alias="apiKey")]]


class DataConnectorGreenhouseDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["greenhouse"]]

    settings: DataConnectorGreenhouseDiscriminatedConnectionSettingsSettings


class DataConnectorHeronDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["heron"]]

    settings: object


class DataConnectorLunchmoneyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["lunchmoney"]]

    settings: object


class DataConnectorMercuryDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["mercury"]]

    settings: object


class DataConnectorMergeDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    account_token: Required[Annotated[str, PropertyInfo(alias="accountToken")]]

    account_details: Annotated[object, PropertyInfo(alias="accountDetails")]


class DataConnectorMergeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["merge"]]

    settings: DataConnectorMergeDiscriminatedConnectionSettingsSettings


class DataConnectorMootaDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["moota"]]

    settings: object


class DataConnectorOnebrickDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    access_token: Required[Annotated[str, PropertyInfo(alias="accessToken")]]


class DataConnectorOnebrickDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["onebrick"]]

    settings: DataConnectorOnebrickDiscriminatedConnectionSettingsSettings


class DataConnectorOpenledgerDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    entity_id: Required[str]
    """Your entity's identifier, aka customer ID"""


class DataConnectorOpenledgerDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["openledger"]]

    settings: DataConnectorOpenledgerDiscriminatedConnectionSettingsSettings


class DataConnectorPlaidDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    access_token: Required[Annotated[str, PropertyInfo(alias="accessToken")]]

    institution: object

    item: object

    item_id: Annotated[Optional[str], PropertyInfo(alias="itemId")]

    status: object

    webhook_item_error: Annotated[None, PropertyInfo(alias="webhookItemError")]


class DataConnectorPlaidDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["plaid"]]

    settings: DataConnectorPlaidDiscriminatedConnectionSettingsSettings


class DataConnectorPostgresDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    database_url: Annotated[str, PropertyInfo(alias="databaseURL")]


class DataConnectorPostgresDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["postgres"]]

    settings: DataConnectorPostgresDiscriminatedConnectionSettingsSettings


class DataConnectorRampDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    access_token: Annotated[Optional[str], PropertyInfo(alias="accessToken")]

    start_after_transaction_id: Annotated[Optional[str], PropertyInfo(alias="startAfterTransactionId")]


class DataConnectorRampDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["ramp"]]

    settings: DataConnectorRampDiscriminatedConnectionSettingsSettings


class DataConnectorSaltedgeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["saltedge"]]

    settings: object


class DataConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserNotifications(TypedDict, total=False):
    added_as_friend: Required[bool]

    added_to_group: Required[bool]

    announcements: Required[bool]

    bills: Required[bool]

    expense_added: Required[bool]

    expense_updated: Required[bool]

    monthly_summary: Required[bool]

    payments: Required[bool]


class DataConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserPicture(TypedDict, total=False):
    large: Optional[str]

    medium: Optional[str]

    original: Optional[str]

    small: Optional[str]

    xlarge: Optional[str]

    xxlarge: Optional[str]


class DataConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUser(TypedDict, total=False):
    id: Required[float]

    country_code: Required[str]

    custom_picture: Required[bool]

    date_format: Required[str]

    default_currency: Required[str]

    default_group_id: Required[float]

    email: Required[str]

    first_name: Required[str]

    force_refresh_at: Required[str]

    last_name: Required[str]

    locale: Required[str]

    notifications: Required[DataConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserNotifications]

    notifications_count: Required[float]

    notifications_read: Required[str]

    picture: Required[DataConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserPicture]

    registration_status: Required[str]


class DataConnectorSplitwiseDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    access_token: Required[Annotated[str, PropertyInfo(alias="accessToken")]]

    current_user: Annotated[
        Optional[DataConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUser],
        PropertyInfo(alias="currentUser"),
    ]


class DataConnectorSplitwiseDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["splitwise"]]

    settings: DataConnectorSplitwiseDiscriminatedConnectionSettingsSettings


class DataConnectorStripeDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    secret_key: Required[Annotated[str, PropertyInfo(alias="secretKey")]]


class DataConnectorStripeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["stripe"]]

    settings: DataConnectorStripeDiscriminatedConnectionSettingsSettings


class DataConnectorTellerDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    token: Required[str]


class DataConnectorTellerDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["teller"]]

    settings: DataConnectorTellerDiscriminatedConnectionSettingsSettings


class DataConnectorTogglDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_token: Required[Annotated[str, PropertyInfo(alias="apiToken")]]

    email: Optional[str]

    password: Optional[str]


class DataConnectorTogglDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["toggl"]]

    settings: DataConnectorTogglDiscriminatedConnectionSettingsSettings


class DataConnectorTwentyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    access_token: Required[str]


class DataConnectorTwentyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["twenty"]]

    settings: DataConnectorTwentyDiscriminatedConnectionSettingsSettings


class DataConnectorVenmoDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    credentials: object

    me: object


class DataConnectorVenmoDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["venmo"]]

    settings: DataConnectorVenmoDiscriminatedConnectionSettingsSettings


class DataConnectorWiseDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    env_name: Required[Annotated[Literal["sandbox", "live"], PropertyInfo(alias="envName")]]

    api_token: Annotated[Optional[str], PropertyInfo(alias="apiToken")]


class DataConnectorWiseDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["wise"]]

    settings: DataConnectorWiseDiscriminatedConnectionSettingsSettings


class DataConnectorYodleeDiscriminatedConnectionSettingsSettingsAccessToken(TypedDict, total=False):
    access_token: Required[Annotated[str, PropertyInfo(alias="accessToken")]]

    expires_in: Required[Annotated[float, PropertyInfo(alias="expiresIn")]]

    issued_at: Required[Annotated[str, PropertyInfo(alias="issuedAt")]]


class DataConnectorYodleeDiscriminatedConnectionSettingsSettingsProviderAccount(TypedDict, total=False):
    id: Required[float]

    aggregation_source: Required[Annotated[str, PropertyInfo(alias="aggregationSource")]]

    created_date: Required[Annotated[str, PropertyInfo(alias="createdDate")]]

    dataset: Required[Iterable[object]]

    is_manual: Required[Annotated[bool, PropertyInfo(alias="isManual")]]

    provider_id: Required[Annotated[float, PropertyInfo(alias="providerId")]]

    status: Required[
        Literal["LOGIN_IN_PROGRESS", "USER_INPUT_REQUIRED", "IN_PROGRESS", "PARTIAL_SUCCESS", "SUCCESS", "FAILED"]
    ]

    is_deleted: Annotated[Optional[bool], PropertyInfo(alias="isDeleted")]


class DataConnectorYodleeDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    login_name: Required[Annotated[str, PropertyInfo(alias="loginName")]]

    provider_account_id: Required[Annotated[Union[float, str], PropertyInfo(alias="providerAccountId")]]

    access_token: Annotated[
        Optional[DataConnectorYodleeDiscriminatedConnectionSettingsSettingsAccessToken],
        PropertyInfo(alias="accessToken"),
    ]

    provider: None

    provider_account: Annotated[
        Optional[DataConnectorYodleeDiscriminatedConnectionSettingsSettingsProviderAccount],
        PropertyInfo(alias="providerAccount"),
    ]

    user: None


class DataConnectorYodleeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["yodlee"]]

    settings: DataConnectorYodleeDiscriminatedConnectionSettingsSettings


Data: TypeAlias = Union[
    DataConnectorAcceloDiscriminatedConnectionSettings,
    DataConnectorAcmeOauth2DiscriminatedConnectionSettings,
    DataConnectorAdobeDiscriminatedConnectionSettings,
    DataConnectorAdyenDiscriminatedConnectionSettings,
    DataConnectorAircallDiscriminatedConnectionSettings,
    DataConnectorAmazonDiscriminatedConnectionSettings,
    DataConnectorApaleoDiscriminatedConnectionSettings,
    DataConnectorAsanaDiscriminatedConnectionSettings,
    DataConnectorAttioDiscriminatedConnectionSettings,
    DataConnectorAuth0DiscriminatedConnectionSettings,
    DataConnectorAutodeskDiscriminatedConnectionSettings,
    DataConnectorAwsDiscriminatedConnectionSettings,
    DataConnectorBamboohrDiscriminatedConnectionSettings,
    DataConnectorBasecampDiscriminatedConnectionSettings,
    DataConnectorBattlenetDiscriminatedConnectionSettings,
    DataConnectorBigcommerceDiscriminatedConnectionSettings,
    DataConnectorBitbucketDiscriminatedConnectionSettings,
    DataConnectorBitlyDiscriminatedConnectionSettings,
    DataConnectorBlackbaudDiscriminatedConnectionSettings,
    DataConnectorBoldsignDiscriminatedConnectionSettings,
    DataConnectorBoxDiscriminatedConnectionSettings,
    DataConnectorBraintreeDiscriminatedConnectionSettings,
    DataConnectorCalendlyDiscriminatedConnectionSettings,
    DataConnectorClickupDiscriminatedConnectionSettings,
    DataConnectorCloseDiscriminatedConnectionSettings,
    DataConnectorConfluenceDiscriminatedConnectionSettings,
    DataConnectorContentfulDiscriminatedConnectionSettings,
    DataConnectorContentstackDiscriminatedConnectionSettings,
    DataConnectorCopperDiscriminatedConnectionSettings,
    DataConnectorCorosDiscriminatedConnectionSettings,
    DataConnectorDatevDiscriminatedConnectionSettings,
    DataConnectorDeelDiscriminatedConnectionSettings,
    DataConnectorDialpadDiscriminatedConnectionSettings,
    DataConnectorDigitaloceanDiscriminatedConnectionSettings,
    DataConnectorDiscordDiscriminatedConnectionSettings,
    DataConnectorDocusignDiscriminatedConnectionSettings,
    DataConnectorDropboxDiscriminatedConnectionSettings,
    DataConnectorEbayDiscriminatedConnectionSettings,
    DataConnectorEgnyteDiscriminatedConnectionSettings,
    DataConnectorEnvoyDiscriminatedConnectionSettings,
    DataConnectorEventbriteDiscriminatedConnectionSettings,
    DataConnectorExistDiscriminatedConnectionSettings,
    DataConnectorFacebookDiscriminatedConnectionSettings,
    DataConnectorFactorialDiscriminatedConnectionSettings,
    DataConnectorFigmaDiscriminatedConnectionSettings,
    DataConnectorFitbitDiscriminatedConnectionSettings,
    DataConnectorFortnoxDiscriminatedConnectionSettings,
    DataConnectorFreshbooksDiscriminatedConnectionSettings,
    DataConnectorFrontDiscriminatedConnectionSettings,
    DataConnectorGitHubDiscriminatedConnectionSettings,
    DataConnectorGitlabDiscriminatedConnectionSettings,
    DataConnectorGongDiscriminatedConnectionSettings,
    DataConnectorGoogleCalendarDiscriminatedConnectionSettings,
    DataConnectorGoogleDocsDiscriminatedConnectionSettings,
    DataConnectorGoogleDriveDiscriminatedConnectionSettings,
    DataConnectorGoogleMailDiscriminatedConnectionSettings,
    DataConnectorGoogleSheetDiscriminatedConnectionSettings,
    DataConnectorGorgiasDiscriminatedConnectionSettings,
    DataConnectorGrainDiscriminatedConnectionSettings,
    DataConnectorGumroadDiscriminatedConnectionSettings,
    DataConnectorGustoDiscriminatedConnectionSettings,
    DataConnectorHarvestDiscriminatedConnectionSettings,
    DataConnectorHighlevelDiscriminatedConnectionSettings,
    DataConnectorHubspotDiscriminatedConnectionSettings,
    DataConnectorInstagramDiscriminatedConnectionSettings,
    DataConnectorIntercomDiscriminatedConnectionSettings,
    DataConnectorJiraDiscriminatedConnectionSettings,
    DataConnectorKeapDiscriminatedConnectionSettings,
    DataConnectorLeverDiscriminatedConnectionSettings,
    DataConnectorLinearDiscriminatedConnectionSettings,
    DataConnectorLinkedinDiscriminatedConnectionSettings,
    DataConnectorLinkhutDiscriminatedConnectionSettings,
    DataConnectorMailchimpDiscriminatedConnectionSettings,
    DataConnectorMiroDiscriminatedConnectionSettings,
    DataConnectorMondayDiscriminatedConnectionSettings,
    DataConnectorMuralDiscriminatedConnectionSettings,
    DataConnectorNamelyDiscriminatedConnectionSettings,
    DataConnectorNationbuilderDiscriminatedConnectionSettings,
    DataConnectorNetsuiteDiscriminatedConnectionSettings,
    DataConnectorNotionDiscriminatedConnectionSettings,
    DataConnectorOdooDiscriminatedConnectionSettings,
    DataConnectorOktaDiscriminatedConnectionSettings,
    DataConnectorOsuDiscriminatedConnectionSettings,
    DataConnectorOuraDiscriminatedConnectionSettings,
    DataConnectorOutreachDiscriminatedConnectionSettings,
    DataConnectorPagerdutyDiscriminatedConnectionSettings,
    DataConnectorPandadocDiscriminatedConnectionSettings,
    DataConnectorPayfitDiscriminatedConnectionSettings,
    DataConnectorPaypalDiscriminatedConnectionSettings,
    DataConnectorPennylaneDiscriminatedConnectionSettings,
    DataConnectorPinterestDiscriminatedConnectionSettings,
    DataConnectorPipedriveDiscriminatedConnectionSettings,
    DataConnectorPodiumDiscriminatedConnectionSettings,
    DataConnectorProductboardDiscriminatedConnectionSettings,
    DataConnectorQualtricsDiscriminatedConnectionSettings,
    DataConnectorQuickbooksDiscriminatedConnectionSettings,
    DataConnectorRedditDiscriminatedConnectionSettings,
    DataConnectorSageDiscriminatedConnectionSettings,
    DataConnectorSalesforceDiscriminatedConnectionSettings,
    DataConnectorSalesloftDiscriminatedConnectionSettings,
    DataConnectorSegmentDiscriminatedConnectionSettings,
    DataConnectorServicem8DiscriminatedConnectionSettings,
    DataConnectorServicenowDiscriminatedConnectionSettings,
    DataConnectorSharepointDiscriminatedConnectionSettings,
    DataConnectorShopifyDiscriminatedConnectionSettings,
    DataConnectorSignnowDiscriminatedConnectionSettings,
    DataConnectorSlackDiscriminatedConnectionSettings,
    DataConnectorSmartsheetDiscriminatedConnectionSettings,
    DataConnectorSnowflakeDiscriminatedConnectionSettings,
    DataConnectorSpotifyDiscriminatedConnectionSettings,
    DataConnectorSquarespaceDiscriminatedConnectionSettings,
    DataConnectorSquareupDiscriminatedConnectionSettings,
    DataConnectorStackexchangeDiscriminatedConnectionSettings,
    DataConnectorStravaDiscriminatedConnectionSettings,
    DataConnectorTeamworkDiscriminatedConnectionSettings,
    DataConnectorTicktickDiscriminatedConnectionSettings,
    DataConnectorTimelyDiscriminatedConnectionSettings,
    DataConnectorTodoistDiscriminatedConnectionSettings,
    DataConnectorTremendousDiscriminatedConnectionSettings,
    DataConnectorTsheetsteamDiscriminatedConnectionSettings,
    DataConnectorTumblrDiscriminatedConnectionSettings,
    DataConnectorTwinfieldDiscriminatedConnectionSettings,
    DataConnectorTwitchDiscriminatedConnectionSettings,
    DataConnectorTwitterDiscriminatedConnectionSettings,
    DataConnectorTypeformDiscriminatedConnectionSettings,
    DataConnectorUberDiscriminatedConnectionSettings,
    DataConnectorVimeoDiscriminatedConnectionSettings,
    DataConnectorWakatimeDiscriminatedConnectionSettings,
    DataConnectorWealthboxDiscriminatedConnectionSettings,
    DataConnectorWebflowDiscriminatedConnectionSettings,
    DataConnectorWhoopDiscriminatedConnectionSettings,
    DataConnectorWordpressDiscriminatedConnectionSettings,
    DataConnectorWrikeDiscriminatedConnectionSettings,
    DataConnectorXeroDiscriminatedConnectionSettings,
    DataConnectorYahooDiscriminatedConnectionSettings,
    DataConnectorYandexDiscriminatedConnectionSettings,
    DataConnectorZapierDiscriminatedConnectionSettings,
    DataConnectorZendeskDiscriminatedConnectionSettings,
    DataConnectorZenefitsDiscriminatedConnectionSettings,
    DataConnectorZohoDeskDiscriminatedConnectionSettings,
    DataConnectorZohoDiscriminatedConnectionSettings,
    DataConnectorZoomDiscriminatedConnectionSettings,
    DataConnectorAirtableDiscriminatedConnectionSettings,
    DataConnectorApolloDiscriminatedConnectionSettings,
    DataConnectorBrexDiscriminatedConnectionSettings,
    DataConnectorCodaDiscriminatedConnectionSettings,
    DataConnectorFinchDiscriminatedConnectionSettings,
    DataConnectorFirebaseDiscriminatedConnectionSettings,
    DataConnectorForeceiptDiscriminatedConnectionSettings,
    DataConnectorGreenhouseDiscriminatedConnectionSettings,
    DataConnectorHeronDiscriminatedConnectionSettings,
    DataConnectorLunchmoneyDiscriminatedConnectionSettings,
    DataConnectorMercuryDiscriminatedConnectionSettings,
    DataConnectorMergeDiscriminatedConnectionSettings,
    DataConnectorMootaDiscriminatedConnectionSettings,
    DataConnectorOnebrickDiscriminatedConnectionSettings,
    DataConnectorOpenledgerDiscriminatedConnectionSettings,
    DataConnectorPlaidDiscriminatedConnectionSettings,
    DataConnectorPostgresDiscriminatedConnectionSettings,
    DataConnectorRampDiscriminatedConnectionSettings,
    DataConnectorSaltedgeDiscriminatedConnectionSettings,
    DataConnectorSplitwiseDiscriminatedConnectionSettings,
    DataConnectorStripeDiscriminatedConnectionSettings,
    DataConnectorTellerDiscriminatedConnectionSettings,
    DataConnectorTogglDiscriminatedConnectionSettings,
    DataConnectorTwentyDiscriminatedConnectionSettings,
    DataConnectorVenmoDiscriminatedConnectionSettings,
    DataConnectorWiseDiscriminatedConnectionSettings,
    DataConnectorYodleeDiscriminatedConnectionSettings,
]
