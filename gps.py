import serial
import time
import webbrowser


def parse_gps(raw_val, direction):
    if not raw_val or raw_val.strip() == "":
        return None
    val_float = float(raw_val)
    degrees = int(val_float / 100)
    minutes = val_float - (degrees * 100)
    decimal_degrees = degrees + (minutes / 60)
    if direction == "S" or direction == "W":
        decimal_degrees = -decimal_degrees
    return round(decimal_degrees, 6)


def get_location():
    with serial.Serial("/dev/ttyUSB2", 115200, timeout=2) as ser:
        ser.write(b"AT+CGPS=1\r\n")
        time.sleep(1)
        ser.read_all()

        ser.write(b"AT+CGPSINFO\r\n")
        time.sleep(1)
        response = ser.read_all().decode("utf-8", errors="ignore")

        for line in response.split("\n"):
            if "+CGPSINFO:" in line:
                data = line.replace("+CGPSINFO:", "").strip()

                # Count commas to ensure we have a full dataset
                if data.count(",") >= 4:
                    # Unpack values directly by position to bypass index stripping bugs
                    (
                        raw_lat,
                        lat_dir,
                        raw_lon,
                        lon_dir,
                        *remainder,
                    ) = data.split(",")

                    lat = parse_gps(raw_lat, lat_dir)
                    lon = parse_gps(raw_lon, lon_dir)
                    return lat, lon
    return None, None


if __name__ == "__main__":
    lat, lon = get_location()
    if lat and lon:
        # Construct the URL using direct variables to prevent formatting manipulation
        final_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        print("URL Generated: " + final_url)
        webbrowser.open(final_url)
    else:
        print("No valid fix received from the module yet.")
