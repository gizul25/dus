workspace "Name" "Description" {
    !identifiers hierarchical

    model {
        user = person "User" "Standard employee using height-adjustable desks"
        admin = person "Admin" "Configures the system, monitors the system, and resolves desk issues"
        desk_rest_api = softwareSystem "Desk REST API server" "LINAK height-adjustable desks"
        ss = softwareSystem "Application Software System" {
            group "Server" {
                load_balancer = container "Load balancer" "Expose website to the network and split request load between service instances" "Nginx in development Kubernetes in production"
                frontend = container "Frontend server" "Serve frontend content" "Svelte"
                apache_kafka = container "Apache Kafka" "Responsible for forwarding messages between different services" "custom container in dev apache/kafka in prod"
                mqtt_broker = container "MQTT Broker" "Communicate with Raspberry Pi Pico with MQTT packets" "eclipse-mosquitto"
                mongo_db = container "MongoDB" "Stores all application data" "mongo" {
                    tags "Database"
                }
                
                backend_services = container "Backend services" "Performs actions and provide interface to the database" "Python" {
                    user_service = component "UserService" "Anything that modifies \"User\" entity goes through this handler. This includes CRUD for users and authentication."
                    desk_profile_service = component "DeskProfileService" "This service only has one responsibility - CRUD for desk profiles."
                    desk_service = component "DeskService" "This includes CRUD for desks for admins, automatic controlling of desk height, updating desired target height from manual adjustments, and other parameters."
                    timer_service = component "TimerService" "Responsible for CRUD (no update tho) for timers, and sending event once timer timestamp is reached."
                    desk_issue_service = component "DeskIssueService" "Responsible for CRUD for desk issues, sending notifications to admin when issues arise, and sending notifications to reporters when issues are resolved."
                    pico_environmental_data_ingestion_service = component "PicoEnvironmentalDataIngestionService" "Responsible for getting environmental data from Pico device, and storing it in the database."
                    desk_data_ingestion_service = component "DeskDataIngestionService" "Responsible for collecting the data from all desk REST APIs, storing them in a database, and sending relevant events."
                    desk_session_service = component "DeskSessionService" "Fully responsible for check-in/check-out, handling automatic timeouts, and updating user status based on desk activity and user interaction."
                    office_map_service = component "OfficeMapService" "Responsible for office map page backend."
                    statistics_service = component "StatisticsService" "Responsible for statistics page backend."
                    health_reminder_service = component "HealthReminderService" "Fully responsible for handling all health related functionalities: tracking sitting and standing timers, sending notifications, changing profiles automatically, pausing health timers, and determining middle desk height threshold."
                    pico_peripherals_service = component "PicoPeripheralsService" "Responsible to track events to desk status and health reminders to set correct desk Pico LED colour, and RFID check-in/check-out."
                    frontend_telemetry_service = component "FrontendTelemetryService" "Responsible for capturing frontend errors, and sending them to backend to be stored in a database."
                    
                    desk_issue_service -> user_service "Get user"
                    desk_profile_service -> user_service "Get user"
                    desk_session_service -> user_service "Get user"
                    health_reminder_service -> user_service "Get user"
                    pico_peripherals_service -> user_service "Get user card ID"
                    desk_service -> desk_profile_service "Get desk profile"
                    desk_session_service -> desk_profile_service "Get desk profile"
                    health_reminder_service -> desk_profile_service "Get desk profile"
                    desk_issue_service -> desk_service "Get desk"
                    pico_environmental_data_ingestion_service -> desk_service "Get desk"
                    desk_data_ingestion_service -> desk_service "Get desk"
                    desk_session_service -> desk_service "Control desk profiles"
                    health_reminder_service -> desk_service "Set desk profiles"
                    desk_data_ingestion_service -> timer_service "Set periodic poll timer"
                    desk_session_service -> timer_service "Set automatic timeout timer"
                    health_reminder_service -> timer_service "Set health timers"
                    office_map_service -> desk_issue_service "Get desk issues"
                    statistics_service -> desk_issue_service "Get desk issues"
                    office_map_service -> pico_environmental_data_ingestion_service "Get current/historic data"
                    statistics_service -> pico_environmental_data_ingestion_service "Get historic data"
                    office_map_service -> desk_data_ingestion_service "Get current/historic data"
                    statistics_service -> desk_data_ingestion_service "Get historic data"
                    office_map_service -> desk_session_service "Get desk sessions"
                    statistics_service -> desk_session_service "Get historic desk sessions"
                    pico_peripherals_service -> desk_session_service "Set check-in/check-out"
                    health_reminder_service -> desk_session_service "Pause on \"away\" user status"
                    pico_peripherals_service -> health_reminder_service "Get health reminder state"
                }
                websocket_connection_service = container "WebSocketConnectionService" "Manages persistent WebSocket connections without termination" "Python"

                load_balancer -> websocket_connection_service "Set/get realtime messages" "WSS"
                load_balancer -> backend_services "Get data and perform actions" "HTTPS"
                load_balancer -> frontend "Get website assets" "HTTPS"

                websocket_connection_service -> backend_services.user_service "Authenticate user"
                backend_services.office_map_service -> websocket_connection_service "Update office map changes realtime"
                backend_services.desk_issue_service -> websocket_connection_service "Send notification about issue creation/completion"
                backend_services.desk_service -> websocket_connection_service "Control/get desk height control and get timeout warning notifications"
                backend_services.health_reminder_service -> websocket_connection_service "Send health reminders and automatic change warnings"
            }
            
            web_app = container "Web Application" "Provides an user interface to get data and perform actions" "User browser, JS/TS, Svelte"
            raspberry_pi_pico = container "Raspberry Pi Pico" "Gets environmental data, controls LED, and handles RFID check-in/check-out" "C/C++"
            
            web_app -> load_balancer "Goes through" "HTTPS/WSS"
            
            backend_services -> mqtt_broker "Change Pico status and get data" "TCP TLS"
            backend_services -> apache_kafka "Push/pull messages to/from other services" "TCP"
            backend_services -> mongo_db "Store data" "TCP"
            websocket_connection_service -> mongo_db "Store data" "TCP"
            websocket_connection_service -> apache_kafka "Send/get WebSocket messages" "TCP"
            mqtt_broker -> raspberry_pi_pico "Change Pico status and get data" "TCP TLS"
        }

        user -> ss.web_app "Uses" "HTTPS/WSS"
        admin -> ss.web_app "Uses" "HTTPS/WSS"
        ss.backend_services -> desk_rest_api "Control desk height and get data" "HTTPS"
    }

    views {
        systemContext ss "Diagram1" {
            include *
        }

        container ss "c4_diagram_container" {
            include *
        }
        
        component ss.backend_services "c4_diagram_component" {
            include *
        }

        styles {
            element "Element" {
                color #0773af
                stroke #0773af
                strokeWidth 7
                shape roundedbox
            }
            element "Person" {
                shape person
            }
            element "Database" {
                shape cylinder
            }
            element "Boundary" {
                strokeWidth 5
            }
            relationship "Relationship" {
                thickness 4
            }
        }
    }
}