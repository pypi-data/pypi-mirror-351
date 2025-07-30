# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Union, Optional
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .oauth_connection_settings import OAuthConnectionSettings

__all__ = [
    "CreateConnectionResponse",
    "ConnectorAcceloDiscriminatedConnectionSettings",
    "ConnectorAcceloDiscriminatedConnectionSettingsSettings",
    "ConnectorAcmeOauth2DiscriminatedConnectionSettings",
    "ConnectorAcmeOauth2DiscriminatedConnectionSettingsSettings",
    "ConnectorAdobeDiscriminatedConnectionSettings",
    "ConnectorAdobeDiscriminatedConnectionSettingsSettings",
    "ConnectorAdyenDiscriminatedConnectionSettings",
    "ConnectorAdyenDiscriminatedConnectionSettingsSettings",
    "ConnectorAircallDiscriminatedConnectionSettings",
    "ConnectorAircallDiscriminatedConnectionSettingsSettings",
    "ConnectorAmazonDiscriminatedConnectionSettings",
    "ConnectorAmazonDiscriminatedConnectionSettingsSettings",
    "ConnectorApaleoDiscriminatedConnectionSettings",
    "ConnectorApaleoDiscriminatedConnectionSettingsSettings",
    "ConnectorAsanaDiscriminatedConnectionSettings",
    "ConnectorAsanaDiscriminatedConnectionSettingsSettings",
    "ConnectorAttioDiscriminatedConnectionSettings",
    "ConnectorAttioDiscriminatedConnectionSettingsSettings",
    "ConnectorAuth0DiscriminatedConnectionSettings",
    "ConnectorAuth0DiscriminatedConnectionSettingsSettings",
    "ConnectorAutodeskDiscriminatedConnectionSettings",
    "ConnectorAutodeskDiscriminatedConnectionSettingsSettings",
    "ConnectorAwsDiscriminatedConnectionSettings",
    "ConnectorAwsDiscriminatedConnectionSettingsSettings",
    "ConnectorBamboohrDiscriminatedConnectionSettings",
    "ConnectorBamboohrDiscriminatedConnectionSettingsSettings",
    "ConnectorBasecampDiscriminatedConnectionSettings",
    "ConnectorBasecampDiscriminatedConnectionSettingsSettings",
    "ConnectorBattlenetDiscriminatedConnectionSettings",
    "ConnectorBattlenetDiscriminatedConnectionSettingsSettings",
    "ConnectorBigcommerceDiscriminatedConnectionSettings",
    "ConnectorBigcommerceDiscriminatedConnectionSettingsSettings",
    "ConnectorBitbucketDiscriminatedConnectionSettings",
    "ConnectorBitbucketDiscriminatedConnectionSettingsSettings",
    "ConnectorBitlyDiscriminatedConnectionSettings",
    "ConnectorBitlyDiscriminatedConnectionSettingsSettings",
    "ConnectorBlackbaudDiscriminatedConnectionSettings",
    "ConnectorBlackbaudDiscriminatedConnectionSettingsSettings",
    "ConnectorBoldsignDiscriminatedConnectionSettings",
    "ConnectorBoldsignDiscriminatedConnectionSettingsSettings",
    "ConnectorBoxDiscriminatedConnectionSettings",
    "ConnectorBoxDiscriminatedConnectionSettingsSettings",
    "ConnectorBraintreeDiscriminatedConnectionSettings",
    "ConnectorBraintreeDiscriminatedConnectionSettingsSettings",
    "ConnectorCalendlyDiscriminatedConnectionSettings",
    "ConnectorCalendlyDiscriminatedConnectionSettingsSettings",
    "ConnectorClickupDiscriminatedConnectionSettings",
    "ConnectorClickupDiscriminatedConnectionSettingsSettings",
    "ConnectorCloseDiscriminatedConnectionSettings",
    "ConnectorCloseDiscriminatedConnectionSettingsSettings",
    "ConnectorConfluenceDiscriminatedConnectionSettings",
    "ConnectorConfluenceDiscriminatedConnectionSettingsSettings",
    "ConnectorContentfulDiscriminatedConnectionSettings",
    "ConnectorContentfulDiscriminatedConnectionSettingsSettings",
    "ConnectorContentstackDiscriminatedConnectionSettings",
    "ConnectorContentstackDiscriminatedConnectionSettingsSettings",
    "ConnectorCopperDiscriminatedConnectionSettings",
    "ConnectorCopperDiscriminatedConnectionSettingsSettings",
    "ConnectorCorosDiscriminatedConnectionSettings",
    "ConnectorCorosDiscriminatedConnectionSettingsSettings",
    "ConnectorDatevDiscriminatedConnectionSettings",
    "ConnectorDatevDiscriminatedConnectionSettingsSettings",
    "ConnectorDeelDiscriminatedConnectionSettings",
    "ConnectorDeelDiscriminatedConnectionSettingsSettings",
    "ConnectorDialpadDiscriminatedConnectionSettings",
    "ConnectorDialpadDiscriminatedConnectionSettingsSettings",
    "ConnectorDigitaloceanDiscriminatedConnectionSettings",
    "ConnectorDigitaloceanDiscriminatedConnectionSettingsSettings",
    "ConnectorDiscordDiscriminatedConnectionSettings",
    "ConnectorDiscordDiscriminatedConnectionSettingsSettings",
    "ConnectorDocusignDiscriminatedConnectionSettings",
    "ConnectorDocusignDiscriminatedConnectionSettingsSettings",
    "ConnectorDropboxDiscriminatedConnectionSettings",
    "ConnectorDropboxDiscriminatedConnectionSettingsSettings",
    "ConnectorEbayDiscriminatedConnectionSettings",
    "ConnectorEbayDiscriminatedConnectionSettingsSettings",
    "ConnectorEgnyteDiscriminatedConnectionSettings",
    "ConnectorEgnyteDiscriminatedConnectionSettingsSettings",
    "ConnectorEnvoyDiscriminatedConnectionSettings",
    "ConnectorEnvoyDiscriminatedConnectionSettingsSettings",
    "ConnectorEventbriteDiscriminatedConnectionSettings",
    "ConnectorEventbriteDiscriminatedConnectionSettingsSettings",
    "ConnectorExistDiscriminatedConnectionSettings",
    "ConnectorExistDiscriminatedConnectionSettingsSettings",
    "ConnectorFacebookDiscriminatedConnectionSettings",
    "ConnectorFacebookDiscriminatedConnectionSettingsSettings",
    "ConnectorFactorialDiscriminatedConnectionSettings",
    "ConnectorFactorialDiscriminatedConnectionSettingsSettings",
    "ConnectorFigmaDiscriminatedConnectionSettings",
    "ConnectorFigmaDiscriminatedConnectionSettingsSettings",
    "ConnectorFitbitDiscriminatedConnectionSettings",
    "ConnectorFitbitDiscriminatedConnectionSettingsSettings",
    "ConnectorFortnoxDiscriminatedConnectionSettings",
    "ConnectorFortnoxDiscriminatedConnectionSettingsSettings",
    "ConnectorFreshbooksDiscriminatedConnectionSettings",
    "ConnectorFreshbooksDiscriminatedConnectionSettingsSettings",
    "ConnectorFrontDiscriminatedConnectionSettings",
    "ConnectorFrontDiscriminatedConnectionSettingsSettings",
    "ConnectorGitHubDiscriminatedConnectionSettings",
    "ConnectorGitHubDiscriminatedConnectionSettingsSettings",
    "ConnectorGitlabDiscriminatedConnectionSettings",
    "ConnectorGitlabDiscriminatedConnectionSettingsSettings",
    "ConnectorGongDiscriminatedConnectionSettings",
    "ConnectorGongDiscriminatedConnectionSettingsSettings",
    "ConnectorGoogleCalendarDiscriminatedConnectionSettings",
    "ConnectorGoogleCalendarDiscriminatedConnectionSettingsSettings",
    "ConnectorGoogleDocsDiscriminatedConnectionSettings",
    "ConnectorGoogleDocsDiscriminatedConnectionSettingsSettings",
    "ConnectorGoogleDriveDiscriminatedConnectionSettings",
    "ConnectorGoogleDriveDiscriminatedConnectionSettingsSettings",
    "ConnectorGoogleMailDiscriminatedConnectionSettings",
    "ConnectorGoogleMailDiscriminatedConnectionSettingsSettings",
    "ConnectorGoogleSheetDiscriminatedConnectionSettings",
    "ConnectorGoogleSheetDiscriminatedConnectionSettingsSettings",
    "ConnectorGorgiasDiscriminatedConnectionSettings",
    "ConnectorGorgiasDiscriminatedConnectionSettingsSettings",
    "ConnectorGrainDiscriminatedConnectionSettings",
    "ConnectorGrainDiscriminatedConnectionSettingsSettings",
    "ConnectorGumroadDiscriminatedConnectionSettings",
    "ConnectorGumroadDiscriminatedConnectionSettingsSettings",
    "ConnectorGustoDiscriminatedConnectionSettings",
    "ConnectorGustoDiscriminatedConnectionSettingsSettings",
    "ConnectorHarvestDiscriminatedConnectionSettings",
    "ConnectorHarvestDiscriminatedConnectionSettingsSettings",
    "ConnectorHighlevelDiscriminatedConnectionSettings",
    "ConnectorHighlevelDiscriminatedConnectionSettingsSettings",
    "ConnectorHubspotDiscriminatedConnectionSettings",
    "ConnectorHubspotDiscriminatedConnectionSettingsSettings",
    "ConnectorInstagramDiscriminatedConnectionSettings",
    "ConnectorInstagramDiscriminatedConnectionSettingsSettings",
    "ConnectorIntercomDiscriminatedConnectionSettings",
    "ConnectorIntercomDiscriminatedConnectionSettingsSettings",
    "ConnectorJiraDiscriminatedConnectionSettings",
    "ConnectorJiraDiscriminatedConnectionSettingsSettings",
    "ConnectorKeapDiscriminatedConnectionSettings",
    "ConnectorKeapDiscriminatedConnectionSettingsSettings",
    "ConnectorLeverDiscriminatedConnectionSettings",
    "ConnectorLeverDiscriminatedConnectionSettingsSettings",
    "ConnectorLinearDiscriminatedConnectionSettings",
    "ConnectorLinearDiscriminatedConnectionSettingsSettings",
    "ConnectorLinkedinDiscriminatedConnectionSettings",
    "ConnectorLinkedinDiscriminatedConnectionSettingsSettings",
    "ConnectorLinkhutDiscriminatedConnectionSettings",
    "ConnectorLinkhutDiscriminatedConnectionSettingsSettings",
    "ConnectorMailchimpDiscriminatedConnectionSettings",
    "ConnectorMailchimpDiscriminatedConnectionSettingsSettings",
    "ConnectorMiroDiscriminatedConnectionSettings",
    "ConnectorMiroDiscriminatedConnectionSettingsSettings",
    "ConnectorMondayDiscriminatedConnectionSettings",
    "ConnectorMondayDiscriminatedConnectionSettingsSettings",
    "ConnectorMuralDiscriminatedConnectionSettings",
    "ConnectorMuralDiscriminatedConnectionSettingsSettings",
    "ConnectorNamelyDiscriminatedConnectionSettings",
    "ConnectorNamelyDiscriminatedConnectionSettingsSettings",
    "ConnectorNationbuilderDiscriminatedConnectionSettings",
    "ConnectorNationbuilderDiscriminatedConnectionSettingsSettings",
    "ConnectorNetsuiteDiscriminatedConnectionSettings",
    "ConnectorNetsuiteDiscriminatedConnectionSettingsSettings",
    "ConnectorNotionDiscriminatedConnectionSettings",
    "ConnectorNotionDiscriminatedConnectionSettingsSettings",
    "ConnectorOdooDiscriminatedConnectionSettings",
    "ConnectorOdooDiscriminatedConnectionSettingsSettings",
    "ConnectorOktaDiscriminatedConnectionSettings",
    "ConnectorOktaDiscriminatedConnectionSettingsSettings",
    "ConnectorOsuDiscriminatedConnectionSettings",
    "ConnectorOsuDiscriminatedConnectionSettingsSettings",
    "ConnectorOuraDiscriminatedConnectionSettings",
    "ConnectorOuraDiscriminatedConnectionSettingsSettings",
    "ConnectorOutreachDiscriminatedConnectionSettings",
    "ConnectorOutreachDiscriminatedConnectionSettingsSettings",
    "ConnectorPagerdutyDiscriminatedConnectionSettings",
    "ConnectorPagerdutyDiscriminatedConnectionSettingsSettings",
    "ConnectorPandadocDiscriminatedConnectionSettings",
    "ConnectorPandadocDiscriminatedConnectionSettingsSettings",
    "ConnectorPayfitDiscriminatedConnectionSettings",
    "ConnectorPayfitDiscriminatedConnectionSettingsSettings",
    "ConnectorPaypalDiscriminatedConnectionSettings",
    "ConnectorPaypalDiscriminatedConnectionSettingsSettings",
    "ConnectorPennylaneDiscriminatedConnectionSettings",
    "ConnectorPennylaneDiscriminatedConnectionSettingsSettings",
    "ConnectorPinterestDiscriminatedConnectionSettings",
    "ConnectorPinterestDiscriminatedConnectionSettingsSettings",
    "ConnectorPipedriveDiscriminatedConnectionSettings",
    "ConnectorPipedriveDiscriminatedConnectionSettingsSettings",
    "ConnectorPodiumDiscriminatedConnectionSettings",
    "ConnectorPodiumDiscriminatedConnectionSettingsSettings",
    "ConnectorProductboardDiscriminatedConnectionSettings",
    "ConnectorProductboardDiscriminatedConnectionSettingsSettings",
    "ConnectorQualtricsDiscriminatedConnectionSettings",
    "ConnectorQualtricsDiscriminatedConnectionSettingsSettings",
    "ConnectorQuickbooksDiscriminatedConnectionSettings",
    "ConnectorQuickbooksDiscriminatedConnectionSettingsSettings",
    "ConnectorRedditDiscriminatedConnectionSettings",
    "ConnectorRedditDiscriminatedConnectionSettingsSettings",
    "ConnectorSageDiscriminatedConnectionSettings",
    "ConnectorSageDiscriminatedConnectionSettingsSettings",
    "ConnectorSalesforceDiscriminatedConnectionSettings",
    "ConnectorSalesforceDiscriminatedConnectionSettingsSettings",
    "ConnectorSalesloftDiscriminatedConnectionSettings",
    "ConnectorSalesloftDiscriminatedConnectionSettingsSettings",
    "ConnectorSegmentDiscriminatedConnectionSettings",
    "ConnectorSegmentDiscriminatedConnectionSettingsSettings",
    "ConnectorServicem8DiscriminatedConnectionSettings",
    "ConnectorServicem8DiscriminatedConnectionSettingsSettings",
    "ConnectorServicenowDiscriminatedConnectionSettings",
    "ConnectorServicenowDiscriminatedConnectionSettingsSettings",
    "ConnectorSharepointDiscriminatedConnectionSettings",
    "ConnectorSharepointDiscriminatedConnectionSettingsSettings",
    "ConnectorShopifyDiscriminatedConnectionSettings",
    "ConnectorShopifyDiscriminatedConnectionSettingsSettings",
    "ConnectorSignnowDiscriminatedConnectionSettings",
    "ConnectorSignnowDiscriminatedConnectionSettingsSettings",
    "ConnectorSlackDiscriminatedConnectionSettings",
    "ConnectorSlackDiscriminatedConnectionSettingsSettings",
    "ConnectorSmartsheetDiscriminatedConnectionSettings",
    "ConnectorSmartsheetDiscriminatedConnectionSettingsSettings",
    "ConnectorSnowflakeDiscriminatedConnectionSettings",
    "ConnectorSnowflakeDiscriminatedConnectionSettingsSettings",
    "ConnectorSpotifyDiscriminatedConnectionSettings",
    "ConnectorSpotifyDiscriminatedConnectionSettingsSettings",
    "ConnectorSquarespaceDiscriminatedConnectionSettings",
    "ConnectorSquarespaceDiscriminatedConnectionSettingsSettings",
    "ConnectorSquareupDiscriminatedConnectionSettings",
    "ConnectorSquareupDiscriminatedConnectionSettingsSettings",
    "ConnectorStackexchangeDiscriminatedConnectionSettings",
    "ConnectorStackexchangeDiscriminatedConnectionSettingsSettings",
    "ConnectorStravaDiscriminatedConnectionSettings",
    "ConnectorStravaDiscriminatedConnectionSettingsSettings",
    "ConnectorTeamworkDiscriminatedConnectionSettings",
    "ConnectorTeamworkDiscriminatedConnectionSettingsSettings",
    "ConnectorTicktickDiscriminatedConnectionSettings",
    "ConnectorTicktickDiscriminatedConnectionSettingsSettings",
    "ConnectorTimelyDiscriminatedConnectionSettings",
    "ConnectorTimelyDiscriminatedConnectionSettingsSettings",
    "ConnectorTodoistDiscriminatedConnectionSettings",
    "ConnectorTodoistDiscriminatedConnectionSettingsSettings",
    "ConnectorTremendousDiscriminatedConnectionSettings",
    "ConnectorTremendousDiscriminatedConnectionSettingsSettings",
    "ConnectorTsheetsteamDiscriminatedConnectionSettings",
    "ConnectorTsheetsteamDiscriminatedConnectionSettingsSettings",
    "ConnectorTumblrDiscriminatedConnectionSettings",
    "ConnectorTumblrDiscriminatedConnectionSettingsSettings",
    "ConnectorTwinfieldDiscriminatedConnectionSettings",
    "ConnectorTwinfieldDiscriminatedConnectionSettingsSettings",
    "ConnectorTwitchDiscriminatedConnectionSettings",
    "ConnectorTwitchDiscriminatedConnectionSettingsSettings",
    "ConnectorTwitterDiscriminatedConnectionSettings",
    "ConnectorTwitterDiscriminatedConnectionSettingsSettings",
    "ConnectorTypeformDiscriminatedConnectionSettings",
    "ConnectorTypeformDiscriminatedConnectionSettingsSettings",
    "ConnectorUberDiscriminatedConnectionSettings",
    "ConnectorUberDiscriminatedConnectionSettingsSettings",
    "ConnectorVimeoDiscriminatedConnectionSettings",
    "ConnectorVimeoDiscriminatedConnectionSettingsSettings",
    "ConnectorWakatimeDiscriminatedConnectionSettings",
    "ConnectorWakatimeDiscriminatedConnectionSettingsSettings",
    "ConnectorWealthboxDiscriminatedConnectionSettings",
    "ConnectorWealthboxDiscriminatedConnectionSettingsSettings",
    "ConnectorWebflowDiscriminatedConnectionSettings",
    "ConnectorWebflowDiscriminatedConnectionSettingsSettings",
    "ConnectorWhoopDiscriminatedConnectionSettings",
    "ConnectorWhoopDiscriminatedConnectionSettingsSettings",
    "ConnectorWordpressDiscriminatedConnectionSettings",
    "ConnectorWordpressDiscriminatedConnectionSettingsSettings",
    "ConnectorWrikeDiscriminatedConnectionSettings",
    "ConnectorWrikeDiscriminatedConnectionSettingsSettings",
    "ConnectorXeroDiscriminatedConnectionSettings",
    "ConnectorXeroDiscriminatedConnectionSettingsSettings",
    "ConnectorYahooDiscriminatedConnectionSettings",
    "ConnectorYahooDiscriminatedConnectionSettingsSettings",
    "ConnectorYandexDiscriminatedConnectionSettings",
    "ConnectorYandexDiscriminatedConnectionSettingsSettings",
    "ConnectorZapierDiscriminatedConnectionSettings",
    "ConnectorZapierDiscriminatedConnectionSettingsSettings",
    "ConnectorZendeskDiscriminatedConnectionSettings",
    "ConnectorZendeskDiscriminatedConnectionSettingsSettings",
    "ConnectorZenefitsDiscriminatedConnectionSettings",
    "ConnectorZenefitsDiscriminatedConnectionSettingsSettings",
    "ConnectorZohoDeskDiscriminatedConnectionSettings",
    "ConnectorZohoDeskDiscriminatedConnectionSettingsSettings",
    "ConnectorZohoDiscriminatedConnectionSettings",
    "ConnectorZohoDiscriminatedConnectionSettingsSettings",
    "ConnectorZoomDiscriminatedConnectionSettings",
    "ConnectorZoomDiscriminatedConnectionSettingsSettings",
    "ConnectorAirtableDiscriminatedConnectionSettings",
    "ConnectorAirtableDiscriminatedConnectionSettingsSettings",
    "ConnectorApolloDiscriminatedConnectionSettings",
    "ConnectorApolloDiscriminatedConnectionSettingsSettings",
    "ConnectorBrexDiscriminatedConnectionSettings",
    "ConnectorBrexDiscriminatedConnectionSettingsSettings",
    "ConnectorCodaDiscriminatedConnectionSettings",
    "ConnectorCodaDiscriminatedConnectionSettingsSettings",
    "ConnectorFinchDiscriminatedConnectionSettings",
    "ConnectorFinchDiscriminatedConnectionSettingsSettings",
    "ConnectorFirebaseDiscriminatedConnectionSettings",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettings",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0ServiceAccount",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthData",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJson",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember1",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember2",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1FirebaseConfig",
    "ConnectorForeceiptDiscriminatedConnectionSettings",
    "ConnectorForeceiptDiscriminatedConnectionSettingsSettings",
    "ConnectorGreenhouseDiscriminatedConnectionSettings",
    "ConnectorGreenhouseDiscriminatedConnectionSettingsSettings",
    "ConnectorHeronDiscriminatedConnectionSettings",
    "ConnectorLunchmoneyDiscriminatedConnectionSettings",
    "ConnectorMercuryDiscriminatedConnectionSettings",
    "ConnectorMergeDiscriminatedConnectionSettings",
    "ConnectorMergeDiscriminatedConnectionSettingsSettings",
    "ConnectorMootaDiscriminatedConnectionSettings",
    "ConnectorOnebrickDiscriminatedConnectionSettings",
    "ConnectorOnebrickDiscriminatedConnectionSettingsSettings",
    "ConnectorOpenledgerDiscriminatedConnectionSettings",
    "ConnectorOpenledgerDiscriminatedConnectionSettingsSettings",
    "ConnectorPlaidDiscriminatedConnectionSettings",
    "ConnectorPlaidDiscriminatedConnectionSettingsSettings",
    "ConnectorPostgresDiscriminatedConnectionSettings",
    "ConnectorPostgresDiscriminatedConnectionSettingsSettings",
    "ConnectorRampDiscriminatedConnectionSettings",
    "ConnectorRampDiscriminatedConnectionSettingsSettings",
    "ConnectorSaltedgeDiscriminatedConnectionSettings",
    "ConnectorSplitwiseDiscriminatedConnectionSettings",
    "ConnectorSplitwiseDiscriminatedConnectionSettingsSettings",
    "ConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUser",
    "ConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserNotifications",
    "ConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserPicture",
    "ConnectorStripeDiscriminatedConnectionSettings",
    "ConnectorStripeDiscriminatedConnectionSettingsSettings",
    "ConnectorTellerDiscriminatedConnectionSettings",
    "ConnectorTellerDiscriminatedConnectionSettingsSettings",
    "ConnectorTogglDiscriminatedConnectionSettings",
    "ConnectorTogglDiscriminatedConnectionSettingsSettings",
    "ConnectorTwentyDiscriminatedConnectionSettings",
    "ConnectorTwentyDiscriminatedConnectionSettingsSettings",
    "ConnectorVenmoDiscriminatedConnectionSettings",
    "ConnectorVenmoDiscriminatedConnectionSettingsSettings",
    "ConnectorWiseDiscriminatedConnectionSettings",
    "ConnectorWiseDiscriminatedConnectionSettingsSettings",
    "ConnectorYodleeDiscriminatedConnectionSettings",
    "ConnectorYodleeDiscriminatedConnectionSettingsSettings",
    "ConnectorYodleeDiscriminatedConnectionSettingsSettingsAccessToken",
    "ConnectorYodleeDiscriminatedConnectionSettingsSettingsProviderAccount",
]


class ConnectorAcceloDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    subdomain: str
    """The subdomain of your Accelo account (e.g., https://domain.api.accelo.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAcceloDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["accelo"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAcceloDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAcmeOauth2DiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAcmeOauth2DiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["acme-oauth2"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAcmeOauth2DiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAdobeDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAdobeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["adobe"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAdobeDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAdyenDiscriminatedConnectionSettingsSettings(BaseModel):
    environment: str
    """The environment to use (e.g., live|test)"""

    oauth: OAuthConnectionSettings

    resource: str
    """
    The resource to use for your various requests (e.g.,
    https://kyc-(live|test).adyen.com)
    """

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAdyenDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["adyen"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAdyenDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAircallDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAircallDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["aircall"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAircallDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAmazonDiscriminatedConnectionSettingsSettings(BaseModel):
    extension: str
    """The domain extension for your Amazon account (e.g., com)"""

    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAmazonDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["amazon"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAmazonDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorApaleoDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorApaleoDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["apaleo"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorApaleoDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAsanaDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAsanaDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["asana"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAsanaDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAttioDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAttioDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["attio"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAttioDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAuth0DiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    subdomain: str
    """The subdomain of your Auth0 account (e.g., https://domain.auth0.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAuth0DiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["auth0"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAuth0DiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAutodeskDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAutodeskDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["autodesk"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAutodeskDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAwsDiscriminatedConnectionSettingsSettings(BaseModel):
    api_subdomain: str = FieldInfo(alias="apiSubdomain")
    """
    The API subdomain to the API you want to connect to (e.g.,
    https://cognito-idp.us-east-2.amazonaws.com)
    """

    extension: str
    """The domain extension of your AWS account (e.g., com)"""

    oauth: OAuthConnectionSettings

    subdomain: str
    """The subdomain of your AWS account (e.g., https://domain.amazoncognito.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAwsDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["aws"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAwsDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBamboohrDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    subdomain: str
    """The subdomain of your BambooHR account (e.g., https://domain.bamboohr.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBamboohrDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["bamboohr"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBamboohrDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBasecampDiscriminatedConnectionSettingsSettings(BaseModel):
    account_id: str = FieldInfo(alias="accountId")
    """Your Account ID (e.g., 5899981)"""

    app_details: str = FieldInfo(alias="appDetails")
    """The details of your app (e.g., example-subdomain)"""

    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBasecampDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["basecamp"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBasecampDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBattlenetDiscriminatedConnectionSettingsSettings(BaseModel):
    api_domain: str = FieldInfo(alias="apiDomain")
    """
    The domain to where you will access your API (e.g., https://us.api.blizzard.com)
    """

    extension: str
    """The domain extension of your Battle.net account (e.g., com)"""

    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBattlenetDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["battlenet"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBattlenetDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBigcommerceDiscriminatedConnectionSettingsSettings(BaseModel):
    account_uuid: str = FieldInfo(alias="accountUuid")
    """
    The account UUID of your BigCommerce account (e.g.,
    123e4567-e89b-12d3-a456-426614174000)
    """

    oauth: OAuthConnectionSettings

    store_hash: str = FieldInfo(alias="storeHash")
    """The store hash of your BigCommerce account (e.g., Example123)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBigcommerceDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["bigcommerce"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBigcommerceDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBitbucketDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBitbucketDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["bitbucket"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBitbucketDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBitlyDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBitlyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["bitly"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBitlyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBlackbaudDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBlackbaudDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["blackbaud"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBlackbaudDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBoldsignDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBoldsignDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["boldsign"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBoldsignDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBoxDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBoxDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["box"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBoxDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBraintreeDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBraintreeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["braintree"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBraintreeDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorCalendlyDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorCalendlyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["calendly"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorCalendlyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorClickupDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorClickupDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["clickup"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorClickupDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorCloseDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorCloseDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["close"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorCloseDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorConfluenceDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorConfluenceDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["confluence"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorConfluenceDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorContentfulDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    subdomain: str
    """The subdomain of your Contentful account (e.g., https://domain.contentful.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorContentfulDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["contentful"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorContentfulDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorContentstackDiscriminatedConnectionSettingsSettings(BaseModel):
    api_domain: str = FieldInfo(alias="apiDomain")
    """
    The domain to where you will access your API (e.g.,
    https://eu-api.contentstack.com)
    """

    app_id: str = FieldInfo(alias="appId")
    """The app ID of your Contentstack account (e.g., example-subdomain)"""

    oauth: OAuthConnectionSettings

    subdomain: str
    """
    The subdomain of your Contentstack account (e.g.,
    https://domain.contentstack.com)
    """

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorContentstackDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["contentstack"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorContentstackDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorCopperDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorCopperDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["copper"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorCopperDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorCorosDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorCorosDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["coros"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorCorosDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDatevDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorDatevDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["datev"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorDatevDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDeelDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorDeelDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["deel"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorDeelDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDialpadDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorDialpadDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["dialpad"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorDialpadDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDigitaloceanDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorDigitaloceanDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["digitalocean"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorDigitaloceanDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDiscordDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorDiscordDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["discord"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorDiscordDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDocusignDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorDocusignDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["docusign"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorDocusignDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDropboxDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorDropboxDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["dropbox"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorDropboxDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorEbayDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorEbayDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["ebay"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorEbayDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorEgnyteDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    subdomain: str
    """The subdomain of your Egnyte account (e.g., https://domain.egnyte.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorEgnyteDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["egnyte"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorEgnyteDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorEnvoyDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorEnvoyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["envoy"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorEnvoyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorEventbriteDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorEventbriteDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["eventbrite"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorEventbriteDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorExistDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorExistDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["exist"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorExistDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFacebookDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorFacebookDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["facebook"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorFacebookDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFactorialDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorFactorialDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["factorial"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorFactorialDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFigmaDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorFigmaDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["figma"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorFigmaDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFitbitDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorFitbitDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["fitbit"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorFitbitDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFortnoxDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorFortnoxDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["fortnox"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorFortnoxDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFreshbooksDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorFreshbooksDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["freshbooks"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorFreshbooksDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFrontDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorFrontDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["front"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorFrontDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGitHubDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGitHubDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["github"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGitHubDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGitlabDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGitlabDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["gitlab"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGitlabDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGongDiscriminatedConnectionSettingsSettings(BaseModel):
    api_base_url_for_customer: str
    """The base URL of your Gong account (e.g., example)"""

    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGongDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["gong"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGongDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGoogleCalendarDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGoogleCalendarDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["google-calendar"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGoogleCalendarDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGoogleDocsDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGoogleDocsDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["google-docs"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGoogleDocsDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGoogleDriveDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGoogleDriveDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["google-drive"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGoogleDriveDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGoogleMailDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGoogleMailDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["google-mail"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGoogleMailDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGoogleSheetDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGoogleSheetDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["google-sheet"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGoogleSheetDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGorgiasDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    subdomain: str
    """The subdomain of your Gorgias account (e.g., https://domain.gorgias.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGorgiasDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["gorgias"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGorgiasDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGrainDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGrainDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["grain"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGrainDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGumroadDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGumroadDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["gumroad"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGumroadDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGustoDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGustoDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["gusto"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGustoDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorHarvestDiscriminatedConnectionSettingsSettings(BaseModel):
    app_details: str = FieldInfo(alias="appDetails")
    """The details of your app (e.g., example-subdomain)"""

    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorHarvestDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["harvest"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorHarvestDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorHighlevelDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorHighlevelDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["highlevel"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorHighlevelDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorHubspotDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorHubspotDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["hubspot"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorHubspotDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorInstagramDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorInstagramDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["instagram"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorInstagramDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorIntercomDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorIntercomDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["intercom"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorIntercomDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorJiraDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorJiraDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["jira"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorJiraDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorKeapDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorKeapDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["keap"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorKeapDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorLeverDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorLeverDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["lever"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorLeverDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorLinearDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorLinearDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["linear"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorLinearDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorLinkedinDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorLinkedinDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["linkedin"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorLinkedinDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorLinkhutDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorLinkhutDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["linkhut"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorLinkhutDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMailchimpDiscriminatedConnectionSettingsSettings(BaseModel):
    dc: str
    """The data center for your account (e.g., us6)"""

    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorMailchimpDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["mailchimp"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorMailchimpDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMiroDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorMiroDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["miro"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorMiroDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMondayDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorMondayDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["monday"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorMondayDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMuralDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorMuralDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["mural"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorMuralDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorNamelyDiscriminatedConnectionSettingsSettings(BaseModel):
    company: str
    """The name of your Namely company (e.g., example)"""

    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorNamelyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["namely"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorNamelyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorNationbuilderDiscriminatedConnectionSettingsSettings(BaseModel):
    account_id: str = FieldInfo(alias="accountId")
    """The account ID of your NationBuilder account (e.g., example-subdomain)"""

    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorNationbuilderDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["nationbuilder"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorNationbuilderDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorNetsuiteDiscriminatedConnectionSettingsSettings(BaseModel):
    account_id: str = FieldInfo(alias="accountId")
    """The account ID of your NetSuite account (e.g., tstdrv231585)"""

    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorNetsuiteDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["netsuite"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorNetsuiteDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorNotionDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorNotionDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["notion"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorNotionDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOdooDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    server_url: str = FieldInfo(alias="serverUrl")
    """The domain of your Odoo account (e.g., https://example-subdomain)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorOdooDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["odoo"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorOdooDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOktaDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    subdomain: str
    """The subdomain of your Okta account (e.g., https://domain.okta.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorOktaDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["okta"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorOktaDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOsuDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorOsuDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["osu"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorOsuDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOuraDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorOuraDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["oura"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorOuraDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOutreachDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorOutreachDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["outreach"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorOutreachDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPagerdutyDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorPagerdutyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["pagerduty"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPagerdutyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPandadocDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorPandadocDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["pandadoc"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPandadocDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPayfitDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorPayfitDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["payfit"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPayfitDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPaypalDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorPaypalDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["paypal"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPaypalDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPennylaneDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorPennylaneDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["pennylane"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPennylaneDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPinterestDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorPinterestDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["pinterest"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPinterestDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPipedriveDiscriminatedConnectionSettingsSettings(BaseModel):
    api_domain: str
    """The API URL of your Pipedrive account (e.g., example)"""

    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorPipedriveDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["pipedrive"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPipedriveDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPodiumDiscriminatedConnectionSettingsSettings(BaseModel):
    api_version: str = FieldInfo(alias="apiVersion")
    """The API version of your Podium account (e.g., example-subdomain)"""

    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorPodiumDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["podium"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPodiumDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorProductboardDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorProductboardDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["productboard"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorProductboardDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorQualtricsDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    subdomain: str
    """The subdomain of your Qualtrics account (e.g., https://domain.qualtrics.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorQualtricsDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["qualtrics"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorQualtricsDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorQuickbooksDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorQuickbooksDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["quickbooks"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorQuickbooksDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorRedditDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorRedditDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["reddit"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorRedditDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSageDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSageDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["sage"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSageDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSalesforceDiscriminatedConnectionSettingsSettings(BaseModel):
    instance_url: str
    """The instance URL of your Salesforce account (e.g., example)"""

    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSalesforceDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["salesforce"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSalesforceDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSalesloftDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSalesloftDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["salesloft"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSalesloftDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSegmentDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSegmentDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["segment"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSegmentDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorServicem8DiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorServicem8DiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["servicem8"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorServicem8DiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorServicenowDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    subdomain: str
    """The subdomain of your ServiceNow account (e.g., https://domain.service-now.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorServicenowDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["servicenow"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorServicenowDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSharepointDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSharepointDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["sharepoint"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSharepointDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorShopifyDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    subdomain: str
    """The subdomain of your Shopify account (e.g., https://domain.myshopify.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorShopifyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["shopify"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorShopifyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSignnowDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSignnowDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["signnow"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSignnowDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSlackDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSlackDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["slack"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSlackDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSmartsheetDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSmartsheetDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["smartsheet"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSmartsheetDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSnowflakeDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    snowflake_account_url: str
    """The domain of your Snowflake account (e.g., https://example-subdomain)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSnowflakeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["snowflake"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSnowflakeDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSpotifyDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSpotifyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["spotify"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSpotifyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSquarespaceDiscriminatedConnectionSettingsSettings(BaseModel):
    customapp_description: str = FieldInfo(alias="customappDescription")
    """The user agent of your custom app (e.g., example-subdomain)"""

    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSquarespaceDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["squarespace"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSquarespaceDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSquareupDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSquareupDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["squareup"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSquareupDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorStackexchangeDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorStackexchangeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["stackexchange"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorStackexchangeDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorStravaDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorStravaDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["strava"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorStravaDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTeamworkDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTeamworkDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["teamwork"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTeamworkDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTicktickDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTicktickDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["ticktick"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTicktickDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTimelyDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTimelyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["timely"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTimelyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTodoistDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTodoistDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["todoist"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTodoistDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTremendousDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTremendousDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["tremendous"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTremendousDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTsheetsteamDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTsheetsteamDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["tsheetsteam"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTsheetsteamDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTumblrDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTumblrDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["tumblr"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTumblrDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTwinfieldDiscriminatedConnectionSettingsSettings(BaseModel):
    cluster: str
    """The cluster to your Twinfield instance (e.g., https://accounting.twinfield.com)"""

    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTwinfieldDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["twinfield"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTwinfieldDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTwitchDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTwitchDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["twitch"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTwitchDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTwitterDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTwitterDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["twitter"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTwitterDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTypeformDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTypeformDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["typeform"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTypeformDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorUberDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorUberDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["uber"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorUberDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorVimeoDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorVimeoDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["vimeo"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorVimeoDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWakatimeDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorWakatimeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["wakatime"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorWakatimeDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWealthboxDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorWealthboxDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["wealthbox"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorWealthboxDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWebflowDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorWebflowDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["webflow"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorWebflowDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWhoopDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorWhoopDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["whoop"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorWhoopDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWordpressDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorWordpressDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["wordpress"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorWordpressDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWrikeDiscriminatedConnectionSettingsSettings(BaseModel):
    host: str
    """The domain of your Wrike account (e.g., https://example-subdomain)"""

    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorWrikeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["wrike"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorWrikeDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorXeroDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorXeroDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["xero"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorXeroDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorYahooDiscriminatedConnectionSettingsSettings(BaseModel):
    api_domain: str = FieldInfo(alias="apiDomain")
    """
    The domain to the API you want to connect to (e.g.,
    https://fantasysports.yahooapis.com)
    """

    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorYahooDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["yahoo"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorYahooDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorYandexDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorYandexDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["yandex"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorYandexDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorZapierDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorZapierDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["zapier"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorZapierDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorZendeskDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    subdomain: str
    """The subdomain of your Zendesk account (e.g., https://domain.zendesk.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorZendeskDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["zendesk"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorZendeskDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorZenefitsDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorZenefitsDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["zenefits"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorZenefitsDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorZohoDeskDiscriminatedConnectionSettingsSettings(BaseModel):
    extension: str
    """The domain extension of your Zoho account (e.g., https://accounts.zoho.com/)"""

    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorZohoDeskDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["zoho-desk"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorZohoDeskDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorZohoDiscriminatedConnectionSettingsSettings(BaseModel):
    extension: str
    """The domain extension of your Zoho account (e.g., https://accounts.zoho.com/)"""

    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorZohoDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["zoho"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorZohoDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorZoomDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: OAuthConnectionSettings

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorZoomDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["zoom"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorZoomDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAirtableDiscriminatedConnectionSettingsSettings(BaseModel):
    airtable_base: str = FieldInfo(alias="airtableBase")

    api_key: str = FieldInfo(alias="apiKey")


class ConnectorAirtableDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["airtable"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAirtableDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorApolloDiscriminatedConnectionSettingsSettings(BaseModel):
    api_key: str


class ConnectorApolloDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["apollo"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorApolloDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBrexDiscriminatedConnectionSettingsSettings(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")


class ConnectorBrexDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["brex"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBrexDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorCodaDiscriminatedConnectionSettingsSettings(BaseModel):
    api_key: str = FieldInfo(alias="apiKey")


class ConnectorCodaDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["coda"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorCodaDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFinchDiscriminatedConnectionSettingsSettings(BaseModel):
    access_token: str


class ConnectorFinchDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["finch"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorFinchDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0ServiceAccount(BaseModel):
    project_id: str

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0(BaseModel):
    role: Literal["admin"]

    service_account: ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0ServiceAccount = FieldInfo(
        alias="serviceAccount"
    )


class ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJson(BaseModel):
    app_name: str = FieldInfo(alias="appName")

    sts_token_manager: Dict[str, object] = FieldInfo(alias="stsTokenManager")

    uid: str

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0(BaseModel):
    method: Literal["userJson"]

    user_json: ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJson = (
        FieldInfo(alias="userJson")
    )


class ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember1(BaseModel):
    custom_token: str = FieldInfo(alias="customToken")

    method: Literal["customToken"]


class ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember2(BaseModel):
    email: str

    method: Literal["emailPassword"]

    password: str


ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthData: TypeAlias = Union[
    ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0,
    ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember1,
    ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember2,
]


class ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1FirebaseConfig(BaseModel):
    api_key: str = FieldInfo(alias="apiKey")

    app_id: str = FieldInfo(alias="appId")

    auth_domain: str = FieldInfo(alias="authDomain")

    database_url: str = FieldInfo(alias="databaseURL")

    project_id: str = FieldInfo(alias="projectId")

    measurement_id: Optional[str] = FieldInfo(alias="measurementId", default=None)

    messaging_sender_id: Optional[str] = FieldInfo(alias="messagingSenderId", default=None)

    storage_bucket: Optional[str] = FieldInfo(alias="storageBucket", default=None)


class ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1(BaseModel):
    auth_data: ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthData = FieldInfo(
        alias="authData"
    )

    firebase_config: ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1FirebaseConfig = FieldInfo(
        alias="firebaseConfig"
    )

    role: Literal["user"]


ConnectorFirebaseDiscriminatedConnectionSettingsSettings: TypeAlias = Union[
    ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0,
    ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1,
]


class ConnectorFirebaseDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["firebase"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorFirebaseDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorForeceiptDiscriminatedConnectionSettingsSettings(BaseModel):
    env_name: Literal["staging", "production"] = FieldInfo(alias="envName")

    api_id: Optional[object] = FieldInfo(alias="_id", default=None)

    credentials: Optional[object] = None


class ConnectorForeceiptDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["foreceipt"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorForeceiptDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGreenhouseDiscriminatedConnectionSettingsSettings(BaseModel):
    api_key: str = FieldInfo(alias="apiKey")


class ConnectorGreenhouseDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["greenhouse"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGreenhouseDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorHeronDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["heron"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[object] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorLunchmoneyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["lunchmoney"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[object] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMercuryDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["mercury"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[object] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMergeDiscriminatedConnectionSettingsSettings(BaseModel):
    account_token: str = FieldInfo(alias="accountToken")

    account_details: Optional[object] = FieldInfo(alias="accountDetails", default=None)


class ConnectorMergeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["merge"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorMergeDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMootaDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["moota"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[object] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOnebrickDiscriminatedConnectionSettingsSettings(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")


class ConnectorOnebrickDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["onebrick"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorOnebrickDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOpenledgerDiscriminatedConnectionSettingsSettings(BaseModel):
    entity_id: str
    """Your entity's identifier, aka customer ID"""


class ConnectorOpenledgerDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["openledger"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorOpenledgerDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPlaidDiscriminatedConnectionSettingsSettings(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")

    institution: Optional[object] = None

    item: Optional[object] = None

    item_id: Optional[str] = FieldInfo(alias="itemId", default=None)

    status: Optional[object] = None

    webhook_item_error: None = FieldInfo(alias="webhookItemError", default=None)


class ConnectorPlaidDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["plaid"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPlaidDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPostgresDiscriminatedConnectionSettingsSettings(BaseModel):
    database_url: Optional[str] = FieldInfo(alias="databaseURL", default=None)


class ConnectorPostgresDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["postgres"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPostgresDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorRampDiscriminatedConnectionSettingsSettings(BaseModel):
    access_token: Optional[str] = FieldInfo(alias="accessToken", default=None)

    start_after_transaction_id: Optional[str] = FieldInfo(alias="startAfterTransactionId", default=None)


class ConnectorRampDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["ramp"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorRampDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSaltedgeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["saltedge"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[object] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserNotifications(BaseModel):
    added_as_friend: bool

    added_to_group: bool

    announcements: bool

    bills: bool

    expense_added: bool

    expense_updated: bool

    monthly_summary: bool

    payments: bool


class ConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserPicture(BaseModel):
    large: Optional[str] = None

    medium: Optional[str] = None

    original: Optional[str] = None

    small: Optional[str] = None

    xlarge: Optional[str] = None

    xxlarge: Optional[str] = None


class ConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUser(BaseModel):
    id: float

    country_code: str

    custom_picture: bool

    date_format: str

    default_currency: str

    default_group_id: float

    email: str

    first_name: str

    force_refresh_at: str

    last_name: str

    locale: str

    notifications: ConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserNotifications

    notifications_count: float

    notifications_read: str

    picture: ConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserPicture

    registration_status: str


class ConnectorSplitwiseDiscriminatedConnectionSettingsSettings(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")

    current_user: Optional[ConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUser] = FieldInfo(
        alias="currentUser", default=None
    )


class ConnectorSplitwiseDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["splitwise"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSplitwiseDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorStripeDiscriminatedConnectionSettingsSettings(BaseModel):
    secret_key: str = FieldInfo(alias="secretKey")


class ConnectorStripeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["stripe"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorStripeDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTellerDiscriminatedConnectionSettingsSettings(BaseModel):
    token: str


class ConnectorTellerDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["teller"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTellerDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTogglDiscriminatedConnectionSettingsSettings(BaseModel):
    api_token: str = FieldInfo(alias="apiToken")

    email: Optional[str] = None

    password: Optional[str] = None


class ConnectorTogglDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["toggl"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTogglDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTwentyDiscriminatedConnectionSettingsSettings(BaseModel):
    access_token: str


class ConnectorTwentyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["twenty"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTwentyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorVenmoDiscriminatedConnectionSettingsSettings(BaseModel):
    credentials: Optional[object] = None

    me: Optional[object] = None


class ConnectorVenmoDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["venmo"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorVenmoDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWiseDiscriminatedConnectionSettingsSettings(BaseModel):
    env_name: Literal["sandbox", "live"] = FieldInfo(alias="envName")

    api_token: Optional[str] = FieldInfo(alias="apiToken", default=None)


class ConnectorWiseDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["wise"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorWiseDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorYodleeDiscriminatedConnectionSettingsSettingsAccessToken(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")

    expires_in: float = FieldInfo(alias="expiresIn")

    issued_at: str = FieldInfo(alias="issuedAt")


class ConnectorYodleeDiscriminatedConnectionSettingsSettingsProviderAccount(BaseModel):
    id: float

    aggregation_source: str = FieldInfo(alias="aggregationSource")

    created_date: str = FieldInfo(alias="createdDate")

    dataset: List[object]

    is_manual: bool = FieldInfo(alias="isManual")

    provider_id: float = FieldInfo(alias="providerId")

    status: Literal["LOGIN_IN_PROGRESS", "USER_INPUT_REQUIRED", "IN_PROGRESS", "PARTIAL_SUCCESS", "SUCCESS", "FAILED"]

    is_deleted: Optional[bool] = FieldInfo(alias="isDeleted", default=None)


class ConnectorYodleeDiscriminatedConnectionSettingsSettings(BaseModel):
    login_name: str = FieldInfo(alias="loginName")

    provider_account_id: Union[float, str] = FieldInfo(alias="providerAccountId")

    access_token: Optional[ConnectorYodleeDiscriminatedConnectionSettingsSettingsAccessToken] = FieldInfo(
        alias="accessToken", default=None
    )

    provider: None = None

    provider_account: Optional[ConnectorYodleeDiscriminatedConnectionSettingsSettingsProviderAccount] = FieldInfo(
        alias="providerAccount", default=None
    )

    user: None = None


class ConnectorYodleeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["yodlee"]

    id: Optional[str] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorYodleeDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


CreateConnectionResponse: TypeAlias = Union[
    ConnectorAcceloDiscriminatedConnectionSettings,
    ConnectorAcmeOauth2DiscriminatedConnectionSettings,
    ConnectorAdobeDiscriminatedConnectionSettings,
    ConnectorAdyenDiscriminatedConnectionSettings,
    ConnectorAircallDiscriminatedConnectionSettings,
    ConnectorAmazonDiscriminatedConnectionSettings,
    ConnectorApaleoDiscriminatedConnectionSettings,
    ConnectorAsanaDiscriminatedConnectionSettings,
    ConnectorAttioDiscriminatedConnectionSettings,
    ConnectorAuth0DiscriminatedConnectionSettings,
    ConnectorAutodeskDiscriminatedConnectionSettings,
    ConnectorAwsDiscriminatedConnectionSettings,
    ConnectorBamboohrDiscriminatedConnectionSettings,
    ConnectorBasecampDiscriminatedConnectionSettings,
    ConnectorBattlenetDiscriminatedConnectionSettings,
    ConnectorBigcommerceDiscriminatedConnectionSettings,
    ConnectorBitbucketDiscriminatedConnectionSettings,
    ConnectorBitlyDiscriminatedConnectionSettings,
    ConnectorBlackbaudDiscriminatedConnectionSettings,
    ConnectorBoldsignDiscriminatedConnectionSettings,
    ConnectorBoxDiscriminatedConnectionSettings,
    ConnectorBraintreeDiscriminatedConnectionSettings,
    ConnectorCalendlyDiscriminatedConnectionSettings,
    ConnectorClickupDiscriminatedConnectionSettings,
    ConnectorCloseDiscriminatedConnectionSettings,
    ConnectorConfluenceDiscriminatedConnectionSettings,
    ConnectorContentfulDiscriminatedConnectionSettings,
    ConnectorContentstackDiscriminatedConnectionSettings,
    ConnectorCopperDiscriminatedConnectionSettings,
    ConnectorCorosDiscriminatedConnectionSettings,
    ConnectorDatevDiscriminatedConnectionSettings,
    ConnectorDeelDiscriminatedConnectionSettings,
    ConnectorDialpadDiscriminatedConnectionSettings,
    ConnectorDigitaloceanDiscriminatedConnectionSettings,
    ConnectorDiscordDiscriminatedConnectionSettings,
    ConnectorDocusignDiscriminatedConnectionSettings,
    ConnectorDropboxDiscriminatedConnectionSettings,
    ConnectorEbayDiscriminatedConnectionSettings,
    ConnectorEgnyteDiscriminatedConnectionSettings,
    ConnectorEnvoyDiscriminatedConnectionSettings,
    ConnectorEventbriteDiscriminatedConnectionSettings,
    ConnectorExistDiscriminatedConnectionSettings,
    ConnectorFacebookDiscriminatedConnectionSettings,
    ConnectorFactorialDiscriminatedConnectionSettings,
    ConnectorFigmaDiscriminatedConnectionSettings,
    ConnectorFitbitDiscriminatedConnectionSettings,
    ConnectorFortnoxDiscriminatedConnectionSettings,
    ConnectorFreshbooksDiscriminatedConnectionSettings,
    ConnectorFrontDiscriminatedConnectionSettings,
    ConnectorGitHubDiscriminatedConnectionSettings,
    ConnectorGitlabDiscriminatedConnectionSettings,
    ConnectorGongDiscriminatedConnectionSettings,
    ConnectorGoogleCalendarDiscriminatedConnectionSettings,
    ConnectorGoogleDocsDiscriminatedConnectionSettings,
    ConnectorGoogleDriveDiscriminatedConnectionSettings,
    ConnectorGoogleMailDiscriminatedConnectionSettings,
    ConnectorGoogleSheetDiscriminatedConnectionSettings,
    ConnectorGorgiasDiscriminatedConnectionSettings,
    ConnectorGrainDiscriminatedConnectionSettings,
    ConnectorGumroadDiscriminatedConnectionSettings,
    ConnectorGustoDiscriminatedConnectionSettings,
    ConnectorHarvestDiscriminatedConnectionSettings,
    ConnectorHighlevelDiscriminatedConnectionSettings,
    ConnectorHubspotDiscriminatedConnectionSettings,
    ConnectorInstagramDiscriminatedConnectionSettings,
    ConnectorIntercomDiscriminatedConnectionSettings,
    ConnectorJiraDiscriminatedConnectionSettings,
    ConnectorKeapDiscriminatedConnectionSettings,
    ConnectorLeverDiscriminatedConnectionSettings,
    ConnectorLinearDiscriminatedConnectionSettings,
    ConnectorLinkedinDiscriminatedConnectionSettings,
    ConnectorLinkhutDiscriminatedConnectionSettings,
    ConnectorMailchimpDiscriminatedConnectionSettings,
    ConnectorMiroDiscriminatedConnectionSettings,
    ConnectorMondayDiscriminatedConnectionSettings,
    ConnectorMuralDiscriminatedConnectionSettings,
    ConnectorNamelyDiscriminatedConnectionSettings,
    ConnectorNationbuilderDiscriminatedConnectionSettings,
    ConnectorNetsuiteDiscriminatedConnectionSettings,
    ConnectorNotionDiscriminatedConnectionSettings,
    ConnectorOdooDiscriminatedConnectionSettings,
    ConnectorOktaDiscriminatedConnectionSettings,
    ConnectorOsuDiscriminatedConnectionSettings,
    ConnectorOuraDiscriminatedConnectionSettings,
    ConnectorOutreachDiscriminatedConnectionSettings,
    ConnectorPagerdutyDiscriminatedConnectionSettings,
    ConnectorPandadocDiscriminatedConnectionSettings,
    ConnectorPayfitDiscriminatedConnectionSettings,
    ConnectorPaypalDiscriminatedConnectionSettings,
    ConnectorPennylaneDiscriminatedConnectionSettings,
    ConnectorPinterestDiscriminatedConnectionSettings,
    ConnectorPipedriveDiscriminatedConnectionSettings,
    ConnectorPodiumDiscriminatedConnectionSettings,
    ConnectorProductboardDiscriminatedConnectionSettings,
    ConnectorQualtricsDiscriminatedConnectionSettings,
    ConnectorQuickbooksDiscriminatedConnectionSettings,
    ConnectorRedditDiscriminatedConnectionSettings,
    ConnectorSageDiscriminatedConnectionSettings,
    ConnectorSalesforceDiscriminatedConnectionSettings,
    ConnectorSalesloftDiscriminatedConnectionSettings,
    ConnectorSegmentDiscriminatedConnectionSettings,
    ConnectorServicem8DiscriminatedConnectionSettings,
    ConnectorServicenowDiscriminatedConnectionSettings,
    ConnectorSharepointDiscriminatedConnectionSettings,
    ConnectorShopifyDiscriminatedConnectionSettings,
    ConnectorSignnowDiscriminatedConnectionSettings,
    ConnectorSlackDiscriminatedConnectionSettings,
    ConnectorSmartsheetDiscriminatedConnectionSettings,
    ConnectorSnowflakeDiscriminatedConnectionSettings,
    ConnectorSpotifyDiscriminatedConnectionSettings,
    ConnectorSquarespaceDiscriminatedConnectionSettings,
    ConnectorSquareupDiscriminatedConnectionSettings,
    ConnectorStackexchangeDiscriminatedConnectionSettings,
    ConnectorStravaDiscriminatedConnectionSettings,
    ConnectorTeamworkDiscriminatedConnectionSettings,
    ConnectorTicktickDiscriminatedConnectionSettings,
    ConnectorTimelyDiscriminatedConnectionSettings,
    ConnectorTodoistDiscriminatedConnectionSettings,
    ConnectorTremendousDiscriminatedConnectionSettings,
    ConnectorTsheetsteamDiscriminatedConnectionSettings,
    ConnectorTumblrDiscriminatedConnectionSettings,
    ConnectorTwinfieldDiscriminatedConnectionSettings,
    ConnectorTwitchDiscriminatedConnectionSettings,
    ConnectorTwitterDiscriminatedConnectionSettings,
    ConnectorTypeformDiscriminatedConnectionSettings,
    ConnectorUberDiscriminatedConnectionSettings,
    ConnectorVimeoDiscriminatedConnectionSettings,
    ConnectorWakatimeDiscriminatedConnectionSettings,
    ConnectorWealthboxDiscriminatedConnectionSettings,
    ConnectorWebflowDiscriminatedConnectionSettings,
    ConnectorWhoopDiscriminatedConnectionSettings,
    ConnectorWordpressDiscriminatedConnectionSettings,
    ConnectorWrikeDiscriminatedConnectionSettings,
    ConnectorXeroDiscriminatedConnectionSettings,
    ConnectorYahooDiscriminatedConnectionSettings,
    ConnectorYandexDiscriminatedConnectionSettings,
    ConnectorZapierDiscriminatedConnectionSettings,
    ConnectorZendeskDiscriminatedConnectionSettings,
    ConnectorZenefitsDiscriminatedConnectionSettings,
    ConnectorZohoDeskDiscriminatedConnectionSettings,
    ConnectorZohoDiscriminatedConnectionSettings,
    ConnectorZoomDiscriminatedConnectionSettings,
    ConnectorAirtableDiscriminatedConnectionSettings,
    ConnectorApolloDiscriminatedConnectionSettings,
    ConnectorBrexDiscriminatedConnectionSettings,
    ConnectorCodaDiscriminatedConnectionSettings,
    ConnectorFinchDiscriminatedConnectionSettings,
    ConnectorFirebaseDiscriminatedConnectionSettings,
    ConnectorForeceiptDiscriminatedConnectionSettings,
    ConnectorGreenhouseDiscriminatedConnectionSettings,
    ConnectorHeronDiscriminatedConnectionSettings,
    ConnectorLunchmoneyDiscriminatedConnectionSettings,
    ConnectorMercuryDiscriminatedConnectionSettings,
    ConnectorMergeDiscriminatedConnectionSettings,
    ConnectorMootaDiscriminatedConnectionSettings,
    ConnectorOnebrickDiscriminatedConnectionSettings,
    ConnectorOpenledgerDiscriminatedConnectionSettings,
    ConnectorPlaidDiscriminatedConnectionSettings,
    ConnectorPostgresDiscriminatedConnectionSettings,
    ConnectorRampDiscriminatedConnectionSettings,
    ConnectorSaltedgeDiscriminatedConnectionSettings,
    ConnectorSplitwiseDiscriminatedConnectionSettings,
    ConnectorStripeDiscriminatedConnectionSettings,
    ConnectorTellerDiscriminatedConnectionSettings,
    ConnectorTogglDiscriminatedConnectionSettings,
    ConnectorTwentyDiscriminatedConnectionSettings,
    ConnectorVenmoDiscriminatedConnectionSettings,
    ConnectorWiseDiscriminatedConnectionSettings,
    ConnectorYodleeDiscriminatedConnectionSettings,
]
