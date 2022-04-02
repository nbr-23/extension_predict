// Copyright (c) Microsoft Corporation.
// Licensed under the MIT license.
// import * as pbi from 'powerbi-client';

$(function () {
    var reportContainer = $("#report-container").get(0);

    // Initialize iframe for embedding report
    powerbi.bootstrap(reportContainer, { type: "report" });    
    
    var models = window["powerbi-client"].models;
    // const models = pbi.models;
    // var models = powerbi.models;
    var reportLoadConfig = {
        type: "report",
        tokenType: models.TokenType.Embed,

        // Enable this setting to remove gray shoulders from embedded report
        // settings: {
        //     background: models.BackgroundType.Transparent
        // }

        settings: {
            panes: {
                filters: {
                    visible: false
                },
                pageNavigation: {
                    // visible: false,
                    position: models.PageNavigationPosition.Left
                }
            }
        }
    };
    
    $.ajax({
        type: "GET",
        url: "/getembedinfo",
        dataType: "json",
        success: function (data) {
            embedData = $.parseJSON(JSON.stringify(data));
            reportLoadConfig.accessToken = embedData.accessToken;

            // You can embed different reports as per your need
            reportLoadConfig.embedUrl = embedData.reportConfig[0].embedUrl;

            // Use the token expiry to regenerate Embed token for seamless end user experience
            // Refer https://aka.ms/RefreshEmbedToken
            tokenExpiry = embedData.tokenExpiry;

            // Embed Power BI report when Access token and Embed URL are available
            var report = powerbi.embed(reportContainer, reportLoadConfig);

            // Displays the report in full screen mode.
            // report.fullscreen();

            // Triggers when a report schema is successfully loaded
            report.on("loaded", function () {
                console.log("Report load successful")
            });

            // Triggers when a report is successfully embedded in UI
            report.on("rendered", function () {
                console.log("Report render successful")
            });

            // report.off removes all event handlers for a specific event
            report.off("pageChanged");

            // report.on will add an event listener.
            report.on("pageChanged", async function (event) {
                let page = event.detail.newPage;
                console.log("Event - pageChanged:\nPage changed to \"" + page.name + "\" - \"" + page.displayName + "\"");

                // bookmarksManager.apply will apply the bookmark with the
                // given name on the report.
                // This is the actual bookmark name not the display name.
                // try {
                //     // let embedConfig = {
                //     //     bookmark: {
                //     //         name: "Bookmark27806b75682529a791d7"
                //     //     }
                //     // };
                //     // report.updateSettings(embedConfig)
                //     await report.bookmarksManager.apply("Bookmark27806b75682529a791d7");
                //     console.log("Bookmark \"Month\" applied.");
                // }
                // catch (errors) {
                //     console.log(errors);
                // }
            });            

            // report.off removes all event handlers for a specific event
            report.off("bookmarkApplied");

            // report.on will add an event listener.
            report.on("bookmarkApplied", function (event) {
                console.log("Event - bookmarkApplied:\n", event.detail);
            });            

            // Clear any other error handler event
            report.off("error");

            // Below patch of code is for handling errors that occur during embedding
            report.on("error", function (event) {
                var errorMsg = event.detail;

                // Use errorMsg variable to log error in any destination of choice
                console.error(errorMsg);
                return;
            });
        },
        error: function (err) {

            // Show error container
            var errorContainer = $(".error-container");
            $(".embed-container").hide();
            errorContainer.show();

            // Format error message
            var errMessageHtml = "<strong> Error Details: </strong> <br/>" + $.parseJSON(err.responseText)["errorMsg"];
            errMessageHtml = errMessageHtml.split("\n").join("<br/>")

            // Show error message on UI
            errorContainer.html(errMessageHtml);
        }
    });
});