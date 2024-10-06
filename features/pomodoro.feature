Feature: Pomodoro Timer

  Scenario: Set a Pomodoro timer for 0 minute(s)
    Given I have set the Pomodoro timer for 0 minute(s)
    When the timer starts
    Then I should hear an alarm sound after 0 minute(s)

  Scenario: Invalid input for timer
    Given I have set the Pomodoro timer for "not_a_number"
    When the timer starts
    Then I should see an error message

  Scenario: No arguments provided
    Given I have not provided any timer arguments
    When the timer starts
    Then I should see an error message
