$(document).ready(function() {
    // When the user clicks the button with id="predictBtn"
    $('#predictBtn').on('click', function() {
        
        // 1. Collect data from input fields
        const userData = {
            flow: $('#flowVolume').val(),
            pressure: $('#staticPressure').val()
        };

        // 2. Show a "Processing" message
        // $('#resultOutput').text('Calculating... please wait.');

        // 3. Send the AJAX POST request to Flask
        $.ajax({
            url: '/predict',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(userData), // Convert JS object to JSON
            success: function(response) {
                // 1. Check if Python said everything is okay
                if (response.status === "success") {
                    
                    // 2. THIS IS WHERE YOU PUT THE CODE
                    // We find the div with id="result" and fill it with your HTML
                    $('#result').html(`
                        <p><strong>Flow Volume:</strong> ${response.flowVolume}</p>
                        <p><strong>Static Pressure:</strong> ${response.staticPressure}</p>
                        <p><strong>Predicted Power:</strong> ${response.prediction} kW</p>
                        <p><strong>Recommended Vendor:</strong> ${response.recommended_vendor}</p>
                    `).show(); // .show() makes the hidden div visible
            
                }
            },
            error: function(error) {
                $('#resultOutput').text('Error: Could not connect to the server.');
                console.log(error);
            }
        });
    });
});