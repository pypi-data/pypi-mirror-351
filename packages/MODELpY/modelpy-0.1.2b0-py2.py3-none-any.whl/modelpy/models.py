from typing import Optional


class Data:
    _data: dict

    def __init__(self, data: dict):
        self._data = data
        for prop, typing in self.__annotations__.items():
            value = data.get(prop)
            if isinstance(value, dict):
                if issubclass(typing, Data):
                    value = typing(value)
            setattr(self, prop, value)

    def __repr__(self):
        return str(self._data)


class GranularAccess(Data):
    hide_private: bool


class ChargeState(Data):
    battery_heater_on: bool
    battery_level: int
    battery_range: float
    charge_amps: int
    charge_current_request: int
    charge_current_request_max: int
    charge_enable_request: bool
    charge_energy_added: float
    charge_limit_soc: int
    charge_limit_soc_max: int
    charge_limit_soc_min: int
    charge_limit_soc_std: int
    charge_miles_added_ideal: float
    charge_miles_added_rated: float
    charge_port_cold_weather_mode: bool
    charge_port_color: str
    charge_port_door_open: bool
    charge_port_latch: str
    charge_rate: int
    charger_actual_current: int
    charger_phases: Optional[int]
    charger_pilot_current: int
    charger_power: int
    charger_voltage: int
    charging_state: str
    conn_charge_cable: str
    est_battery_range: float
    fast_charger_brand: str
    fast_charger_present: bool
    fast_charger_type: str
    ideal_battery_range: float
    managed_charging_active: Optional[bool]
    managed_charging_start_time: Optional[int]
    managed_charging_user_canceled: bool
    max_range_charge_counter: int
    minutes_to_full_charge: int
    not_enough_power_to_heat: Optional[bool]
    off_peak_charging_enabled: bool
    off_peak_charging_times: str
    off_peak_hours_end_time: int
    preconditioning_enabled: bool
    preconditioning_times: str
    scheduled_charging_mode: str
    scheduled_charging_pending: bool
    scheduled_charging_start_time: Optional[int]
    scheduled_departure_time: int
    scheduled_departure_time_minutes: int
    supercharger_session_trip_planner: bool
    time_to_full_charge: int
    timestamp: int
    trip_charging: bool
    usable_battery_level: int
    user_charge_enable_request: Optional[bool]


class ClimateState(Data):
    allow_cabin_overheat_protection: bool
    auto_seat_climate_left: bool
    auto_seat_climate_right: bool
    auto_steering_wheel_heat: bool
    battery_heater: bool
    battery_heater_no_power: Optional[bool]
    bioweapon_mode: bool
    cabin_overheat_protection: str
    cabin_overheat_protection_actively_cooling: bool
    climate_keeper_mode: str
    cop_activation_temperature: str
    defrost_mode: int
    driver_temp_setting: float
    fan_status: int
    hvac_auto_request: str
    inside_temp: float
    is_auto_conditioning_on: bool
    is_climate_on: bool
    is_front_defroster_on: bool
    is_preconditioning: bool
    is_rear_defroster_on: bool
    left_temp_direction: int
    max_avail_temp: int
    min_avail_temp: int
    outside_temp: float
    passenger_temp_setting: float
    remote_heater_control_enabled: bool
    right_temp_direction: int
    seat_heater_left: int
    seat_heater_rear_center: int
    seat_heater_rear_left: int
    seat_heater_rear_right: int
    seat_heater_right: int
    side_mirror_heaters: bool
    steering_wheel_heat_level: int
    steering_wheel_heater: bool
    supports_fan_only_cabin_overheat_protection: bool
    timestamp: int
    wiper_blade_heater: bool


class DriveState(Data):
    active_route_latitude: float
    active_route_longitude: float
    active_route_traffic_minutes_delay: int
    gps_as_of: int
    heading: int
    latitude: float
    longitude: float
    native_latitude: float
    native_location_supported: int
    native_longitude: float
    native_type: str
    power: int
    shift_state: Optional[str]
    speed: Optional[int]
    timestamp: int


class GuiSettings(Data):
    gui_24_hour_time: bool
    gui_charge_rate_units: str
    gui_distance_units: str
    gui_range_display: str
    gui_temperature_units: str
    gui_tirepressure_units: str
    show_range_units: bool
    timestamp: int


class MediaInfo(Data):
    a2dp_source_name: str
    audio_volume: float
    audio_volume_increment: float
    audio_volume_max: float
    media_playback_status: str
    now_playing_album: str
    now_playing_artist: str
    now_playing_duration: int
    now_playing_elapsed: int
    now_playing_source: str
    now_playing_station: str
    now_playing_title: str


class MediaState(Data):
    remote_control_enabled: bool


class SoftwareUpdate(Data):
    download_perc: int
    expected_duration_sec: int
    install_perc: int
    status: str
    version: str


class SpeedLimitMode(Data):
    active: bool
    current_limit_mph: int
    max_limit_mph: int
    min_limit_mph: int
    pin_code_set: bool


class VehicleState(Data):
    api_version: int
    autopark_state_v3: str
    autopark_style: str
    calendar_supported: bool
    car_version: str
    center_display_state: int
    dashcam_clip_save_available: bool
    dashcam_state: str
    df: int
    dr: int
    fd_window: int
    feature_bitmask: str
    fp_window: int
    ft: int
    homelink_device_count: int
    homelink_nearby: bool
    is_user_present: bool
    last_autopark_error: str
    locked: bool
    media_info: MediaInfo
    media_state: MediaState
    notifications_supported: bool
    odometer: float
    parsed_calendar_supported: bool
    pf: int
    pr: int
    rd_window: int
    remote_start: bool
    remote_start_enabled: bool
    remote_start_supported: bool
    rp_window: int
    rt: int
    santa_mode: int
    sentry_mode: bool
    sentry_mode_available: bool
    service_mode: bool
    service_mode_plus: bool
    smart_summon_available: bool
    software_update: SoftwareUpdate
    speed_limit_mode: SpeedLimitMode
    summon_standby_mode_enabled: bool
    timestamp: int
    tpms_hard_warning_fl: bool
    tpms_hard_warning_fr: bool
    tpms_hard_warning_rl: bool
    tpms_hard_warning_rr: bool
    tpms_last_seen_pressure_time_fl: int
    tpms_last_seen_pressure_time_fr: int
    tpms_last_seen_pressure_time_rl: int
    tpms_last_seen_pressure_time_rr: int
    tpms_pressure_fl: float
    tpms_pressure_fr: float
    tpms_pressure_rl: float
    tpms_pressure_rr: float
    tpms_rcp_front_value: float
    tpms_rcp_rear_value: float
    tpms_soft_warning_fl: bool
    tpms_soft_warning_fr: bool
    tpms_soft_warning_rl: bool
    tpms_soft_warning_rr: bool
    valet_mode: bool
    valet_pin_needed: bool
    vehicle_name: str
    vehicle_self_test_progress: int
    vehicle_self_test_requested: bool
    webcam_available: bool


class VehicleConfig(Data):
    aux_park_lamps: str
    badge_version: int
    can_accept_navigation_requests: bool
    can_actuate_trunks: bool
    car_special_type: str
    car_type: str
    charge_port_type: str
    cop_user_set_temp_supported: bool
    dashcam_clip_save_supported: bool
    default_charge_to_max: bool
    driver_assist: str
    ece_restrictions: bool
    efficiency_package: str
    eu_vehicle: bool
    exterior_color: str
    exterior_trim: str
    exterior_trim_override: str
    has_air_suspension: bool
    has_ludicrous_mode: bool
    has_seat_cooling: bool
    headlamp_type: str
    interior_trim_type: str
    key_version: int
    motorized_charge_port: bool
    paint_color_override: str
    performance_package: str
    plg: bool
    pws: bool
    rear_drive_unit: str
    rear_seat_heaters: int
    rear_seat_type: int
    rhd: bool
    roof_color: str
    seat_type: Optional[int]
    spoiler_type: str
    sun_roof_installed: Optional[int]
    supports_qr_pairing: bool
    third_row_seats: str
    timestamp: int
    trim_badging: str
    use_range_badging: bool
    utc_offset: int
    webcam_selfie_supported: bool
    webcam_supported: bool
    wheel_type: str


class Vehicle(Data):
    id: int
    vehicle_id: int
    vin: str
    color: Optional[str]
    access_type: str
    display_name: Optional[str]
    option_codes: Optional[str]
    granular_access: GranularAccess
    tokens: list[str]
    state: str
    in_service: bool
    id_s: str
    calendar_enabled: bool
    api_version: Optional[int]
    backseat_token: Optional[str]
    backseat_token_updated_at: Optional[str]


class VehicleData(Vehicle):
    user_id: int
    charge_state: ChargeState
    climate_state: ClimateState
    drive_state: DriveState
    gui_settings: GuiSettings
    vehicle_config: VehicleConfig
    vehicle_state: VehicleState


class Driver(Data):
    my_tesla_unique_id: int
    user_id: int
    user_id_s: str
    vault_uuid: str
    driver_first_name: str
    driver_last_name: str
    granular_access: GranularAccess
    active_pubkeys: list[str]
    public_key: str


class Billing(Data):
    billingPeriod: str
    currencyCode: str
    optionCode: str
    price: float
    tax: float
    total: float


class Subscription(Data):
    addons: list[Billing]
    billingOptions: list[Billing]
    optionCode: str
    product: str
    startDate: str


class EligibleSubscriptions(Data):
    country: str
    eligible: list[Subscription]
    vin: str


class Pricing(Data):
    price: float
    total: float
    currencyCode: str
    isPrimary: bool


class Upgrade(Data):
    optionCode: str
    optionGroup: str
    currentOptionCode: str
    pricing: list[Pricing]


class EligibleUpgrades(Data):
    vin: str
    country: str
    type: str
    eligible: list[Upgrade]


class VehicleInfo(Data):
    firmware_version: str
    vehicle_command_protocol_required: bool


class FleetStatus(Data):
    key_paired_vins: list[str]
    unpaired_vins: list[str]
    vehicle_info: dict[str, VehicleInfo]


class SkippedVehicles(Data):
    missing_key: list[str]
    unsupported_hardware: list[str]
    unsupported_firmware: list[str]


class FleetUpdateStatus(Data):
    updated_vehicles: int
    skipped_vehicles: Optional[SkippedVehicles]


class FieldSettings(Data):
    interval_seconds: int


class Config(Data):
    hostname: str
    ca: str
    port: int
    exp: Optional[int]
    prefer_typed: Optional[bool]
    fields: dict[str, FieldSettings]
    alert_types: list[str]


class TelemetryConfig(Data):
    """Fleet telemetry config.

    synced set to true means the vehicle has adopted the target config.
    synced set to false means the vehicle will attempt to adopt the target config when it next establishes a backend connection.
    """
    synced: bool
    config: Config


class Code(Data):
    code: str
    colorCode: Optional[str]
    displayName: str
    isActive: bool


class Alert(Data):
    name: str
    time: str
    audience: list[str]
    user_text: str


class ReleaseNote(Data):
    title: str
    subtitle: str
    description: str
    customer_version: str
    icon: str
    image_url: str
    light_image_url: str


class ServiceData(Data):
    service_status: str
    service_etc: str
    service_visit_number: str
    status_id: int


class ShareInvite(Data):
    id: int
    owner_id: int
    share_user_id: Optional[int]
    product_id: str
    expires_at: str
    revoked_at: Optional[str]
    borrowing_device_id: Optional[int]
    key_id: Optional[int]
    product_type: str
    share_type: str
    share_user_sso_id: Optional[int]
    active_pubkeys: list[str]
    id_s: str
    owner_id_s: str
    share_user_id_s: str
    borrowing_key_hash: Optional[str]
    vin: str
    share_link: str


class Warranty(Data):
    warrantyType: str
    warrantyDisplayName: str
    expirationDate: str
    expirationOdometer: int
    odometerUnit: str
    warrantyExpiredOn: Optional[str]
    coverageAgeInYears: int


class WarrantyDetails(Data):
    activeWarranty: list[Warranty]
    upcomingWarranty: list[Warranty]
    expiredWarranty: list[Warranty]


class Location(Data):
    lat: float
    long: float


class DestinationCharging(Data):
    location: Location
    name: str
    type: str
    distance_miles: float
    amenities: str


class Supercharger(Data):
    location: Location
    name: str
    type: str
    distance_miles: float
    available_stalls: int
    total_stalls: int
    site_closed: bool
    amenities: str
    billing_info: str


class ChargingSites(Data):
    congestion_sync_time_utc_secs: int
    destination_charging: list[DestinationCharging]
    superchargers: list[Supercharger]
    timestamp: int
