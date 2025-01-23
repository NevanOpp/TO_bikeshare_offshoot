import Station_List as stations
def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

def get_address_from_user(station_list,input_prompt,test_user_address=None,):
    #get list of addresses form mapbox
    if(test_user_address!= None):
        pass
    else:
        user_address, address_list = input_address_get_coords(station_list,input_prompt)
        print(address_list)

    #get specific address from user
    maxIndex = station_list.get_max_index()
    while True:
        user_response = input("Which of these is the correct address?").lower()
        #if input is valid:
        if user_response.isdigit():
            num = int(user_response)
            if 1 <= num <= maxIndex:
                #return the valid address
                coords, station_address = station_list.return_address(num-1)
                return user_address, coords, station_address

        #otherwise:
        print("Invalid input, please enter a number between 1 and",str(maxIndex))
def input_address_get_coords(station_list,str,test_in=None):
    validAddress = False
    while(validAddress == False):
        #---- For Testing Only 
        if(test_in is not None):
            user_address = test_in
        #----
        else:
            user_address = input(str)
        if(has_numbers(user_address)==False):
            print("Your input must be an address, the API cannot accept place names or other names.")
            continue
        
        else: #this could be called implicitly
            string_address_list = station_list.query_address(user_address)
        if(string_address_list is None):
            print("Invalid address. Please try again.")
            #TODO: More error handling here:
                # - Check if address is in Toronto
                # - Check if address is in Canada
        else:
            validAddress = True
            #print("This is the address we found: ",station_address)
    return user_address,string_address_list
def valid_route(start_station,end_station):
    if(start_station==end_station):
        return False
    return True

def generate_google_maps_url(station_list,start_coords,end_coords):
    return station_list.google_url(station_list.find_nearest_station_id(start_coords[0],start_coords[1]),station_list.find_nearest_station_id(end_coords[0],end_coords[1]))

def main(arg1 = None, arg2 = None,test_mode=False):
    station_list = stations.Station_List(True)
    print("Bike Share Data Loaded")
    print("-----------------------------------")
    runLoop = True
    while(runLoop):
        print("Please enter your start and end address")

        #FOR TESTING ONLY ----------------------
        if test_mode:
            start_address, start_coords = input_address_get_coords(station_list,"Enter the start address: ",arg1)
            end_address, end_coords = input_address_get_coords(station_list,"Enter the end address: ",arg2)
        #----------------------

        else:
            start_address, start_coords, start_station_address = get_address_from_user(station_list,"Enter the start address: ")
            end_address, end_coords, end_station_address = get_address_from_user(station_list,"Enter the end address: ")
        
        if(valid_route(start_address,end_address)):
            print("Route Verified.") #TODO: remove print statement
            runLoop = False
            break
        else:
            print("Start and End address are the same. Please enter two different addresses again.")

    print(f"Start Address: {start_address}, End Address: {end_address}")
    print("Generating Google Maps URL...")
    print(generate_google_maps_url(station_list,start_coords,end_coords))

if __name__ == "__main__":
    print("Welcome to the Bike Share Program!")
    print("Retrieving BikeShare Data... this could take up to 10 seconds")
    main()