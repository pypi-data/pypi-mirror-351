# MODELpY
An unofficial Python library for Tesla's official [Fleet API](https://developer.tesla.com/docs/fleet-api/).

## Supported Functionality
- [X] Authentication
- [X] Fleet Configuration
- [X] Vehicle Endpoints
- [ ] Vehicle Commands
- [ ] Charging Endpoints
- [ ] Energy Endpoints
- [ ] User Endpoints
- [ ] Partner Endpoints

## Features
- Automatically refreshes your token to avoid your code failing after an extended period of time
- All that is needed to start interacting with your Tesla products is a client ID and a refresh token
- JSON responses are return as Models complete with typing
- Full JSON data is also accessible so new API functionality may be immediately supported

## Usage
1. Get a hold of your client ID and refresh token
    - This is done by [Creating an Application](https://developer.tesla.com/docs/fleet-api/getting-started/what-is-fleet-api#step-2-create-an-application)
    - I won't include setup instructions here, but [TeslaMate](https://www.myteslamate.com/) makes it fairly painless
2. Import the TeslaService (and any other service you'll be using) from `modelpy`
    ```python
    from modelpy import TeslaService
    from modelpy.vehicle import VehicleService
    ```
3. Instantiate the TeslaService for your client ID
    ```python
    tesla = TeslaService("abcd1234-5678-9abc-defg-hijklmnopqrst")
    ```
4. Create your other services using the TeslaService
    ```python
    vehicle_service = VehicleService(tesla)
    ```
5. Now you are ready to interact with the API endpoints
    ```python
    from modelpy import TeslaService
    from modelpy.vehicle import VehicleService

    tesla = TeslaService("abcd1234-5678-9abc-defg-hijklmnopqrst")
    vehicle_service = VehicleService(tesla)
    print(vehicle_service.vehicle())
    ```

## TODO
- [ ] Paginated results are not yet supported
- [ ] The North American servers are hardcoded in at the moment
- [ ] Encrypt stored token
- [ ] Use access tokens more and refresh tokens less

## Caveats
- The vehicle subscription endpoints are not supported and will remain that way unless I discover additional documentation
- Your refresh token is stored in plaintext so anyone with access to your device could have full access to your account
- Many scenarios will remain untested as I cannot simulate Tesla's responses with my limited products
- Tesla's docs are sometimes inconsistent or seemingly mistyped, again I can only confirm that I have programmed to align with said documentation
