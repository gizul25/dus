#include "height_control.hpp"

#include <gtest/gtest.h>

#include <limits>
#include <stdexcept>

using height_control::Config;
using height_control::HeightControl;
using height_control::Position;

TEST(HeightControlTest, ClassifiesSittingAndStandingAtInclusiveThresholds) {
    HeightControl control(Config{75.0F, 95.0F, 0});

    EXPECT_EQ(control.update(75.0F, 0), Position::Sitting);
    EXPECT_EQ(control.update(95.0F, 1), Position::Standing);
}

TEST(HeightControlTest, RemainsUnknownBetweenThresholds) {
    HeightControl control;

    EXPECT_EQ(control.update(85.0F, 0), Position::Unknown);
    EXPECT_EQ(control.position(), Position::Unknown);
}

TEST(HeightControlTest, ConfirmsPositionChangeOnlyAfterConfiguredDuration) {
    HeightControl control(Config{70.0F, 100.0F, 5000});

    ASSERT_EQ(control.update(60.0F, 1000), Position::Sitting);
    EXPECT_EQ(control.update(110.0F, 2000), Position::Sitting);
    EXPECT_EQ(control.update(110.0F, 6999), Position::Sitting);
    EXPECT_EQ(control.update(110.0F, 7000), Position::Standing);
}

TEST(HeightControlTest, CancelsPendingChangeWhenHeightReturnsToNeutralRange) {
    HeightControl control(Config{70.0F, 100.0F, 5000});

    ASSERT_EQ(control.update(60.0F, 0), Position::Sitting);
    EXPECT_EQ(control.update(110.0F, 1000), Position::Sitting);
    EXPECT_EQ(control.update(85.0F, 4000), Position::Sitting);
    EXPECT_EQ(control.update(110.0F, 6000), Position::Sitting);
    EXPECT_EQ(control.update(110.0F, 10999), Position::Sitting);
    EXPECT_EQ(control.update(110.0F, 11000), Position::Standing);
}

TEST(HeightControlTest, ChangesPositionImmediatelyWhenConfirmationIsDisabled) {
    HeightControl control(Config{70.0F, 100.0F, 0});

    ASSERT_EQ(control.update(60.0F, 0), Position::Sitting);
    EXPECT_EQ(control.update(110.0F, 1), Position::Standing);
}

TEST(HeightControlTest, RejectsInvalidConfiguration) {
    EXPECT_THROW(HeightControl(Config{100.0F, 100.0F, 5000}), std::invalid_argument);
    EXPECT_THROW(HeightControl(Config{70.0F, 100.0F, 300001}), std::invalid_argument);
}

TEST(HeightControlTest, RejectsInvalidReadingsAndOutOfOrderTimestamps) {
    HeightControl control;

    EXPECT_THROW(control.update(0.0F, 0), std::invalid_argument);
    EXPECT_THROW(control.update(201.0F, 0), std::invalid_argument);
    EXPECT_THROW(
        control.update(std::numeric_limits<float>::quiet_NaN(), 0),
        std::invalid_argument
    );

    ASSERT_EQ(control.update(60.0F, 10), Position::Sitting);
    EXPECT_THROW(control.update(60.0F, 9), std::invalid_argument);
}
