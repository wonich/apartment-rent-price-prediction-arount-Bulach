import streamlit as st
import requests
import matplotlib.pyplot as plt

IMMOLEX_API_KEY = st.secrets["IMMOLEX_API_KEY"]

# Function to make the API request
def get_rent_prediction(data):
    url = "http://api.immolex.ch:8051/predict"  # Your API URL
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": IMMOLEX_API_KEY  # Add the API key header here
    }
    
    payload = {
        "address": data["address"],
        "data": data["features"]
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        
        # Check if the response status is OK (200)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the request: {e}")
        return None

# Streamlit App UI
def app():
    st.title("Apartment Rent Price Prediction - Bülach (CH)")

    # Input fields for apartment features
    st.header("Apartment Details")
    
    address = st.text_input("Where is the appartment located?", "Marktgasse 28, Bülach")

    size_rooms = st.slider("Number of Rooms", min_value=1.0, max_value=5.5, value=2.5, step=0.5)
    size_square_meters = st.slider("Size (m²)", min_value=20, max_value=300, value=70)
    app_count_building = st.slider("Number of Apartments in the Building", min_value=1, max_value=50, value=8)
    floor_numbers = st.slider("Floor of the appartment", min_value=1, max_value=20, value=4)
    age_of_building = st.slider("Age of Building (Years)", min_value=0, max_value=100, value=5)
    penthouse = st.checkbox("Is it a Penthouse?")
    washing_machine = st.checkbox("Has Washing Machine?")
    elevator = st.checkbox("Has Elevator?")
    is_first_rent = st.checkbox("Is it the First Rent?")
    floor_parquet = st.checkbox("Has Parquet Floor?")
    floor_laminate = st.checkbox("Has Laminate Floor?")
    minergie = st.checkbox("Has Minergie Certification?")
    wheelchair_access = st.checkbox("Is it Wheelchair Accessible?")
    garden = st.checkbox("Has Garden?")
    renovate = st.checkbox("Is it Renovated?")
    lakeview = st.checkbox("Has Lake View?")
    lake_access = st.checkbox("Has Lake Access?")
    closet = st.checkbox("Has Closet?")
    screed_basement_storage = st.checkbox("Has Screed or Basement Storage?")
    balcony_terrace = st.checkbox("Has Balcony or Terrace?")
    

    # Prepare the data payload
    features = {
        "sizeRoomsAdvert": size_rooms,
        "sizeSquareMeters": size_square_meters,
        "AppCountOfBuilding": app_count_building,
        "floornumbers": floor_numbers,
        "penthouse": penthouse,
        "washingmachine": washing_machine,
        "elevator": elevator,
        "isfirstrent": is_first_rent,
        "floorparquet": floor_parquet,
        "floorlaminate": floor_laminate,
        "minergie": minergie,
        "wheelchairaccess": wheelchair_access,
        "garden": garden,
        "renovate": renovate,
        "lakeview": lakeview,
        "lakeaccess": lake_access,
        "closet": closet,
        "screedbasementstorage": screed_basement_storage,
        "balconyterrace": balcony_terrace,
        "ageofbuilding": age_of_building
    }

    data = {
        "address": address,
        "features": features
    }

    # When the user presses the button, fetch the prediction
    if st.button("Predict Rent Price"):
        prediction_result = get_rent_prediction(data)

        if prediction_result:
            
            # Show the entire JSON response in a pretty format
            #st.subheader("Raw JSON Response:")
            #st.json(prediction_result)  # Streamlit's json method displays the formatted JSON
            
            prediction = prediction_result["prediction"]
            lower_band = prediction_result["interval"]["lower"]
            upper_band = prediction_result["interval"]["upper"]
            confidence = prediction_result["interval"]["confidence"]
            unit = prediction_result["interval"]["unit"]

            # Check if the median (prediction) is outside of the confidence interval
            if prediction < lower_band or prediction > upper_band:
                st.error("This configuration cannot be calculated with the current model. Please contact www.immolex.ch for further assistance in obtaining prices for special configurations")
            else:
                st.subheader(f"Predicted Rent: {prediction:.0f} {unit}")
                st.write(f"Confidence Interval: {lower_band:.0f} - {upper_band:.0f} {unit} (Confidence: {confidence})")
            
                # Plot the result
                fig, ax = plt.subplots(figsize=(6, 4))

                # Plot bands and prediction
                ax.fill_between([0, 1], lower_band, upper_band, color="cornflowerblue", alpha=0.4, label=f"Confidence Interval ({confidence})")
                ax.plot([0, 1], [prediction, prediction], color="black", linewidth=2, label="Predicted Rent (Median)")

                ax.set_xlim(0, 1)
                ax.set_ylim(min(lower_band, upper_band) - 100, max(lower_band, upper_band) + 100)
                ax.set_xticks([])
                ax.set_yticks([lower_band, upper_band, prediction])
                ax.set_yticklabels([f"{lower_band:.0f}", f"{upper_band:.0f}", f"{prediction:.0f}"])
                ax.set_title("Apartment Rent Price Prediction", fontsize=16, fontweight="bold")
                ax.set_xlabel('Prediction Interval', fontsize=14)
                ax.set_ylabel(f'Price ({unit})', fontsize=14)

                # Adding gridlines for clarity
                ax.grid(True, linestyle='--', alpha=0.5)
                ax.legend()

                st.pyplot(fig)
                
    # Footer Section
    st.markdown("<hr>", unsafe_allow_html=True)  # Horizontal line
    st.markdown('<p style="text-align: center;">For more informations about the Model have a look at the <a href="https://github.com/wonich/apartment-rent-price-prediction-arount-Bulach">github-Repo</a></p>', unsafe_allow_html=True)    
    st.markdown('<p style="text-align: center;">Data and model are powered by <a href="https://www.immolex.ch"><strong>IMMOLEX</strong></a></p>', unsafe_allow_html=True)
    
# Run the app
if __name__ == "__main__":
    app()
