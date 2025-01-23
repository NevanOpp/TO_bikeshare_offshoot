import Station_List as stations
def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)
def input_address_get_coords(station_list,str,test_in=None):
    validAddress = False
    while(validAddress == False):
        address = test_in
        coords = station_list.address_to_coordinates(address)
        if(coords[0] == "!ON"):
            print("Address is not in Ontario. Please try again.")
        if(coords[0] == "!TO"):
            print("Address is not within the Greater Toronto Area, please try again.")
        elif(coords is None):
            print("Invalid address. Please try again.")
            #TODO: More error handling here:
                # - Check if address is in Toronto
                # - Check if address is in Canada
        else:
            validAddress = True
    return address,coords

def valid_route(start_station,end_station):
    if(start_station==end_station):
        return False
    return True

def generate_google_maps_url(station_list,start_coords,end_coords):
    return station_list.google_url(station_list.find_nearest_station_id(start_coords[0],start_coords[1]),station_list.find_nearest_station_id(end_coords[0],end_coords[1]))

def main(arg1 = None, arg2 = None):
    station_list = stations.Station_List(True)
    print("Bike Share Data Loaded")
    print("-----------------------------------")
    runLoop = True
    #FOR TESTING ONLY ----------------------
    start_address, start_coords = input_address_get_coords(station_list,"Enter the start address: ",arg1)
    end_address, end_coords = input_address_get_coords(station_list,"Enter the end address: ",arg2)
    #----------------------
    if(valid_route(start_address,end_address)):
        print("Route Verified.") #TODO: remove print statement
        runLoop = False
    else:
        print("Start and End address are the same. Please enter two different addresses again.")

    print(f"Start Address: {start_address}, End Address: {end_address}")
    print("Generating Google Maps URL...")
    print(generate_google_maps_url(station_list,start_coords,end_coords))

if __name__ == "__main__":
    test1 = "CN Tower"
    test2 = "111 St. George Street"

    print("Welcome to the Bike Share Program!")
    print("Getting BikeShare Data... this could take up to 10 seconds")
    main(test1,test2)