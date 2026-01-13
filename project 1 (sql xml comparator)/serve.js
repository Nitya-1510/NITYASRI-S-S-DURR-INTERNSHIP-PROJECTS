// $(document).ready(function(){
//     $("#connect").click(function(){
//         console.log('ajax called----')
//         var server_val = $('#server').val()
//         var db_name = $('#database').val()
//         var username = $('#user').val()
//         var password = $('#pass').val()
//         var xml_path = $('#xml').val()
//
//         var data_json = {
//             server_val : server_val,
//             db_name : db_name,
//             username : username,
//             password: password,
//             xml_path: xml_path
//         }
//         $.ajax({
//         type:"POST",
//         url:"/connect",
//         contentType:"application/json",
//         data:JSON.stringify(data_json),
//         success:function(response){
//         var res = response
//         console.log(response,'your func is called----')
//         var tableData = (typeof response === "string") ? JSON.parse(response) : response;
//          myTable.clear().rows.add(tableData).draw();
//          console.log("Success! Table body updated with data.");
//         }
//         })
//     })
// })
// $(document).ready(function() {
//     var myTable = $('#myTable').DataTable({
//         deferRender: true,    // Only renders rows when they are needed for view
//         scrollY: 400,         // Adds a scroll bar
//         scroller: true,       // Helps with large datasets
//         ajax: {
//             url: '/connect',   // Flask endpoint
//             type: 'POST',
//             contentType: "application/json",
//             data: function(d) {
//                 // collect values each time before sending
//                 var data_json = {
//                     server_val: $('#server').val(),
//                     db_name: $('#database').val(),
//                     username: $('#user').val(),
//                     password: $('#pass').val(),
//                     xml_path: $('#xml').val()
//                 };
//                 return JSON.stringify(data_json);
//             },
//             dataSrc: ''   // because Flask returns a list, not nested
//         },
//         columns: [
//             { data: 'formatted_date' },
//             { data: 'value_id' },
//             { data: 'value_number' },
//             { data: 'value_summary' },
//             { data: 'areakey' },
//             { data: 'medium' },
//             { data: 'unit' }
//         ],
//         deferLoading: 0
//     });
//
//     $("#connect").click(function() {
//         console.log('ajax called----');
//         myTable.ajax.reload();  // refresh table with new parameters
//     });
// });

// $(document).ready(function() {
//     // var myTable = $('#myTable').DataTable({
//         deferRender: true;
//         scrollY: 400;
//         scroller: true;
    //     columns: [
    //         { data: 'formatted_date' },
    //         { data: 'value_id' },
    //         { data: 'value_number' },
    //         { data: 'value_summary' },
    //         { data: 'areakey' },
    //         { data: 'medium' },
    //         { data: 'unit' }
    //     ]
    // });

//     $("#connect").click(function() {
//         event.preventDefault();
//     try {
//         console.log('ajax called----');
//
//         var data_json = {
//             server_val: $('#server').val(),
//             db_name: $('#database').val(),
//             username: $('#user').val(),
//             password: $('#pass').val(),
//             xml_path: $('#xml').val()
//         };
//
//         console.log("Payload:", JSON.stringify(data_json));
//
//         $.ajax({
//             url:'/test_api',
//             type:'POST',
//             contentType:"application/json",
//             dataType:"json",
//             data: JSON.stringify(data_json),
//             success:function (response){
//                 console.log("Response object:", response);
//                 console.log("Message:", response.message);
//             },
//             error: function(xhr, status, error) {
//                 console.log("Ajax error:", status, error);
//                 console.log("Response text:", xhr.responseText);
//             }
//         });
//     } catch (e) {
//         console.error("Click handler error:", e);
//     }
// });

//     $("#connect").click(function() {
//         event.preventDefault();
//         console.log('ajax called----');
//
//         var data_json = {
//             server_val: $('#server').val(),
//             db_name: $('#database').val(),
//             username: $('#user').val(),
//             password: $('#pass').val(),
//             xml_path: $('#xml').val()
//         };
//         console.log("Payload:", JSON.stringify(data_json));
//         $.ajax({
//             url:'/test_api',
//             type:'POST',
//             contentType:"application/json",
//             dataType:"json",
//             data:JSON.stringify(data_json),
//             success: function(response) {
//     console.log("Response object:", response);
//     if (response.message) {
//         console.log("Message:", response.message);
//     } else {
//         console.log("No message field found");
//     }
// },
//             error: function(xhr, status, error) {
//             console.log("Error:", status, error);
//         }
//
//         })
//
//         $.ajax({
//             url: '/connect',
//             type: 'POST',
//             contentType: "application/json",
//             dataType:"json",
//             data: JSON.stringify(data_json),
//             success: function(response) {
//                 console.log(response.message)
//                 alert("Data processed successfully!");
//                 // var tableData = (typeof response === "string") ? JSON.parse(response) : response;
//                 // myTable.clear().rows.add(response).draw();
//                 // console.log("Success! Table body updated with data.");
//             },
//             error: function(xhr, status, error) {
//         console.log("Ajax error:", status, error);
//         console.log("Response text:", xhr.responseText);
//     }
//
//         });
//     });
// });

$(document).ready(function() {
    // --- 1. LOGIN PAGE LOGIC ---
    $("#connect").on('click', function(e) {
        e.preventDefault();
        const data_json = {
            server_val: $('#server').val(),
            db_name: $('#database').val(),
            username: $('#user').val(),
            password: $('#pass').val(),
            xml_path: $('#xml').val()
        };

        $.ajax({
            url: '/connect',
            type: 'POST',
            contentType: "application/json",
            data: JSON.stringify(data_json),
            success: function(response) {
                if (response.redirect_url) {
                    window.location.href = response.redirect_url;
                }
            }
        });
    });

    // --- 2. RESULTS PAGE LOGIC (ADD THIS) ---
    // Check if the table exists on the current page
   // if ($('#myTable').length) {
   //      $('#myTable').DataTable({
   //          "deferRender": true,  // Improves performance for large datasets
   //          "dom": "frti",        // f: filter, r: processing, t: table, i: info
   //          "pageLength": 25,
   //          "responsive": true,
   //          "scrollY": "400px",   // Adds the 400px vertical scroll
   //          "scrollCollapse": true,
   //          "scroller": true      // Activates the scroller extension
   //      });
   //  }
});