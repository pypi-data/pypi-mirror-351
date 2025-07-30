from typing import Optional, Any, List
from requests.exceptions import HTTPError

from modelpy import TeslaService, base_url
from modelpy.models import Vehicle, VehicleData, Driver, ChargingSites, Alert, ReleaseNote, ServiceData, ShareInvite, \
    Code, EligibleSubscriptions, EligibleUpgrades, WarrantyDetails, Config, FleetUpdateStatus, FleetStatus, \
    TelemetryConfig


class VehicleAsleepError(Exception):
    """Raised when vehicle is unresponsive to commands"""

    def __init__(self, vehicle_tag: str):
        super().__init__(f"No response from vehicle {vehicle_tag}, it may be asleep")


vehicles_url = base_url + "vehicles"
vin_url = base_url + "dx/vehicles"


class VehicleService:
    """Expands TeslaService to provide functionality specifically for vehicles.

    CAVEAT: The subscription endpoints are not currently supported.

    https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#subscriptions
    https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#subscriptions-set
    https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#vehicle-subscriptions
    https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#vehicle-subscriptions-set
    """
    def __init__(self, tesla_service: TeslaService):
        self.tesla_service = tesla_service

    def _get_for(self, vehicle_tag: Optional[str], path: Optional[str] = None, **params) -> Any:
        """Shortcut function to conduct a GET request for a specific vehicle.

        The first_vin property will be used if a vehicle is not specified.

        :param vehicle_tag: VIN or id field of a vehicle
        :param path: path indicating the action to take upon the vehicle
        :param params: any additional parameters to pass to the endpoint
        :return: The response data which may be of any primitive type but is often a dict
        """
        if not vehicle_tag:
            vehicle_tag = self.first_vin
        try:
            return self.tesla_service.get(vehicles_url, vehicle_tag, path, **params)
        except HTTPError as e:
            if e.response.status_code == 408:
                raise VehicleAsleepError(vehicle_tag) from e
            raise

    def _dx_get_for(self, vin: str, path: str) -> Any:
        """Shortcut function to conduct a GET request against a dx endpoint.

        The first_vin property will be used if a vehicle is not specified.

        :param vin: Vehicle Identification Number to optionally specify a vehicle
        :param path: path indicating the action to take upon the vehicle
        :return: The response data which may be of any primitive type but is often a dict
        """
        if not vin:
            vin = self.first_vin
        return self.tesla_service.get(vin_url, path=path, vin=vin)

    @property
    def first_vin(self) -> str:
        """The first VIN that is found to be associated with the account"""
        vehicles = self.list()
        return vehicles[0].vin if vehicles.count else None


    def list(self, page: Optional[int] = None, per_page: Optional[int] = None) -> list[Vehicle]:
        """Returns vehicles belonging to the account.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#list

        :param page: which numbered page to return (defaults to 1)
        :param per_page: how many results to include in each page (defaults to 100)
        :return: A list of vehicles to which the account has access  # TODO: Paginate return object
        """
        return [Vehicle(data) for data in self.tesla_service.get(vehicles_url, page=page, per_page=per_page)]

    def vehicle(self, vehicle_tag: Optional[str] = None) -> Vehicle:
        """Returns information about a vehicle.

        This call, like many others, is free of charge but is therefore limited.
        Use vehicle_data() to fetch all vehicle information at a cost or fleet telemetry to do so for free.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#vehicle

        :param vehicle_tag: VIN or id field to optionally specify a vehicle
        :return: General information regarding the vehicle
        """
        return Vehicle(self._get_for(vehicle_tag))

    def vehicle_data(self, vehicle_tag: Optional[str] = None) -> VehicleData:
        """Makes a live call to the vehicle to fetch realtime information.

        Regularly polling this endpoint is not recommended and will be expensive.
        Instead, Fleet Telemetry allows the vehicle to push data directly to a server whenever it is online.

        For vehicles running firmware versions 2023.38+, location_data is required to fetch vehicle location.
        This will result in a location sharing icon to show on the vehicle UI.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#vehicle-data

        :param vehicle_tag: VIN or id field to optionally specify a vehicle
        :return: A fully populated snapshot of the vehicle's current state
        """
        return VehicleData(self._get_for(vehicle_tag, "vehicle_data"))

    def drivers(self, vehicle_tag: Optional[str] = None) -> List[Driver]:
        """Returns all allowed drivers for a vehicle.

        This endpoint is only available for the vehicle owner.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#drivers

        :param vehicle_tag: VIN or id field to optionally specify a vehicle
        :return: A list of drivers having access to the vehicle
        """
        return [Driver(data) for data in self._get_for(vehicle_tag, "drivers")]

    def remove_driver(self, vehicle_tag: Optional[str] = None) -> None:
        """Removes driver access from a vehicle.

        Share users can only remove their own access.
        Owners can remove share access or their own.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#drivers-remove

        :param vehicle_tag: VIN or id field to optionally specify a vehicle
        """
        self.tesla_service.delete(vehicles_url, vehicle_tag, "drivers")

    def mobile_enabled(self, vehicle_tag: Optional[str] = None) -> bool:
        """Returns whether or not mobile access is enabled for the vehicle.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#mobile-enabled

        :param vehicle_tag: VIN or id field to optionally specify a vehicle
        :return: True if the vehicle may be accessed via the mobile app
        """
        return self._get_for(vehicle_tag, "mobile_enabled")

    def nearby_charging_sites(self,
            vehicle_tag: Optional[str] = None,
            count: Optional[int] = None,
            detail: Optional[bool] = None,
            radius: Optional[int] = None) -> ChargingSites:
        """Returns the charging sites near the current location of the vehicle.

        NOTE: This endpoint uses the device_data pricing.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#nearby-charging-sites

        :param vehicle_tag: VIN or id field to optionally specify a vehicle
        :param count: number of entities to be returned
        :param detail: True to include site details
        :param radius: search radius in miles
        :return: The charging sites currently around the vehicle
        """
        return ChargingSites(self._get_for(vehicle_tag, "nearby_charging_sites", count=count, detail=detail, radius=radius))

    def recent_alerts(self, vehicle_tag: Optional[str] = None) -> List[Alert]:
        """List of recent alerts.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#recent-alerts

        :param vehicle_tag: VIN or id field to optionally specify a vehicle
        :return: A history of alerts for the vehicle
        """
        return [Alert(data) for data in self._get_for(vehicle_tag, "recent_alerts")["recent_alerts"]]

    def release_notes(self, vehicle_tag: Optional[str] = None, language: Optional[str] = None, staged: Optional[bool] = False) -> List[ReleaseNote]:
        """Returns firmware release notes.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#release-notes

        :param vehicle_tag: VIN or id field to optionally specify a vehicle
        :param language: language locale (need more information)
        :param staged: True to include upcoming software update release notes
        :return: A list of changes associated with each software update
        """
        return [ReleaseNote(data) for data in self._get_for(vehicle_tag, "release_notes", language=language, staged=staged)["response"]["release_notes"]]

    def service_data(self, vehicle_tag: Optional[str] = None) -> ServiceData:
        """Fetches information about the service status of the vehicle.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#service-data

        :param vehicle_tag: VIN or id field to optionally specify a vehicle
        :return: The current service status of the vehicle
        """
        return ServiceData(self._get_for(vehicle_tag, "service_data"))

    def create_share_invite(self, vehicle_tag: Optional[str] = None) -> ShareInvite:
        """Creates a share invite.

        Each invite link is for single-use and expires after 24 hours.
        An account that uses the invite will gain Tesla app access to the vehicle, which allows it to do the following:
            View the live location of the vehicle.
            Send remote commands.
            Download the user's Tesla profile to the vehicle.
        To remove access, use the revoke API.
        If a user does not have the Tesla app installed, they will be directed to https://www.tesla.com/_rs/test for guidance.
        A user can set up their phone as key with the Tesla app when in proximity of the vehicle.
        The app access provides DRIVER privileges, which do not encompass all OWNER features.
        Up to five drivers can be added at a time .
        This API does not require the car to be online.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#share-invites-create
        CAVEAT: Pagination is documented but doesn't make sense here

        :param vehicle_tag: VIN or id field to optionally specify a vehicle
        :return: The newly created share invite
        """
        return ShareInvite(self.tesla_service.post(vehicles_url, vehicle_tag, "invitations"))

    def share_invites(self,
            vehicle_tag: Optional[str] = None,
            page: Optional[int] = None,
            per_page: Optional[int] = None) -> List[ShareInvite]:
        """Returns the active share invites for a vehicle.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#share-invites

        :param vehicle_tag: VIN or id field to optionally specify a vehicle
        :param page: which numbered page to return (defaults to 1)
        :param per_page: how many results to include in each page (defaults to 25?)
        :return: A list of all share invites  # TODO: make this list paginated
        """
        return [ShareInvite(data) for data in self._get_for(vehicle_tag, "invitations", page=page, per_page=per_page)]

    def redeem_invite(self, code: str) -> str:
        """Redeems a share invite.

        Once redeemed, the account will gain access to the vehicle within the Tesla app.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#share-invites-redeem

        :param code: invitation code
        :return: The vehicle VIN
        """
        return self.tesla_service.post(vehicles_url, path="invitations/redeem", code=code)["vin"]

    def revoke_invite(self, invite_id: str, vehicle_tag: Optional[str] = None) -> None:  # TODO: raise Exception on False response
        """Revokes a share invite.

        This invalidates the share and makes the link invalid.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#share-invites-revoke

        :param invite_id: id of share invite
        :param vehicle_tag: VIN or id field to optionally specify a vehicle
        """
        self.tesla_service.post(vehicles_url, vehicle_tag, f"invitations/{invite_id}/revoke")

    def options(self, vin: str = None) -> List[Code]:
        """Returns vehicle option details.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#options

        :param vin: Vehicle Identification Number to optionally specify a vehicle
        :return: All applicable options for the vehicle including weather they arte active
        """
        return [Code(data) for data in self._dx_get_for(vin, "options")["codes"]]

    def eligible_subscriptions(self, vin: str = None) -> EligibleSubscriptions:
        """Returns eligible vehicle subscriptions.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#eligible-subscriptions

        :param vin: Vehicle Identification Number to optionally specify a vehicle
        :return: The possible subscriptions available for the vehicle
        """
        return EligibleSubscriptions(self._dx_get_for(vin, "subscriptions/eligibility"))

    def eligible_upgrades(self, vin: str = None) -> EligibleUpgrades:
        """Returns eligible vehicle upgrades.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#eligible-upgrades

        :param vin: Vehicle Identification Number to optionally specify a vehicle
        :return: The possible upgrades available for the vehicle
        """
        return EligibleUpgrades(self._dx_get_for(vin, "upgrades/eligibility"))

    def warranty_details(self, vin: str = None) -> WarrantyDetails:
        """Returns the warranty information for a vehicle.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#warranty-details

        :param vin: Vehicle Identification Number to optionally specify a vehicle
        :return: All warranty information, active or otherwise
        """
        return WarrantyDetails(self._dx_get_for(vin, "warranty/details"))

    def create_telemetry_config(self, config: Config, vins: List[str]) -> FleetUpdateStatus:
        """Configures vehicles to connect to a self-hosted fleet-telemetry server.

        If any specified VINs are not configured, the response will include skipped_vehicles. VINs may be rejected for a few reasons:

        missing_key: The virtual key has not been added to the vehicle. Distributing a public key.
        unsupported_hardware: Pre-2021 Model S and X are not supported.
        unsupported_firmware:
            If calling directly, vehicles running firmware version earlier than 2023.20.
            If using the vehicle-command HTTP proxy, vehicles running firmware version earlier than 2024.26.
        Fleet Telemetry configuration will automatically be removed if a user revokes an application's access.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#fleet-telemetry-config-create

        :param config: telemetry configuration telling the vehicle how to send updates
        :param vins: Vehicle Identification Numbers to specify vehicles
        :return: The number of vehicles configured and reasoning for any that were skipped
        """
        return FleetUpdateStatus(self.tesla_service.post(vehicles_url, path="fleet_telemetry_config", data={"config": config, "vins": vins}))

    def status(self, vins: List[str]) -> FleetStatus:
        """Checks whether vehicles can accept Tesla commands protocol for the partner's public key

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#fleet-status

        :param vins: Vehicle Identification Numbers to specify vehicles
        :return: The configuration status of the vehicles
        """
        return FleetStatus(self.tesla_service.post(vehicles_url, path="fleet_status", data={"vins": vins}))

    def telemetry_config(self, vehicle_tag: str) -> TelemetryConfig:
        """Fetches a vehicle's fleet telemetry config.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#fleet-telemetry-config-get

        :param vehicle_tag: VIN or id field to optionally specify a vehicle
        :return: The telemetry configuration for the vehicle
        """
        return TelemetryConfig(self._get_for(vehicle_tag, "fleet_status"))

    def delete_telemetry_config(self, vehicle_tag: str) -> int:
        """Removes a telemetry configuration from a vehicle.

        https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints#fleet-telemetry-config-delete

        :param vehicle_tag: VIN or id field to optionally specify a vehicle
        :return: The number of vehicles that were updated
        """
        return self.tesla_service.delete(vehicles_url, vehicle_tag, "fleet_telemetry_config")["updated_vehicles"]
