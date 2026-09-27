import sys

with open("artifacts/mobile/components/DailyRewardBanner.tsx", "r") as f:
    content = f.read()

# Replace import
content = content.replace(
    'import Animated, { useAnimatedStyle, withTiming, useSharedValue, withSequence, Easing } from "react-native-reanimated";',
    'import Animated, { useAnimatedStyle, withTiming, useSharedValue, withSequence, Easing, interpolate } from "react-native-reanimated";'
)

# Find the split point
split_point = "  const animatedTimeStyle = useAnimatedStyle(() => {"

head, tail = content.split(split_point)

new_tail = """  const animatedTimeStyle = useAnimatedStyle(() => {
    return {
      transform: [{ scale: pulseScale.value }],
      opacity: pulseOpacity.value,
    };
  });

  const animatedMedallionStyle = useAnimatedStyle(() => {
    return {
      transform: [{ scale: pulseScale.value }],
    };
  });

  const animatedGlowStyle = useAnimatedStyle(() => {
    return {
      opacity: interpolate(pulseOpacity.value, [0.8, 1], [0.1, 0.25]),
    };
  });
  
  const formatTime = (ms: number) => {
    const totalSeconds = Math.floor(ms / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    
    const pad = (n: number) => n.toString().padStart(2, "0");
    return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
  };
  
  const handleClaimPress = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setModalVisible(true);
  };
  
  const handleConfirmClaim = async () => {
    setClaiming(true);
    const res = await claimDailyReward();
    setClaiming(false);
    
    if (res.success) {
      setModalVisible(false);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } else {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      // Wait a moment then close modal on error so they see the error in the UI
      setTimeout(() => setModalVisible(false), 2000);
    }
  };
  
  if (!dailyReward && !dailyRewardError && isDailyRewardLoading) {
    // Initial load
    return (
      <View style={[styles.container, { backgroundColor: colors.card, borderColor: colors.gold + "30" }]} testID="daily-reward-loading">
        <ActivityIndicator color={colors.gold} />
      </View>
    );
  }
  
  if (dailyRewardError && !dailyReward) {
    return (
      <View style={[styles.container, { backgroundColor: colors.card, borderColor: colors.gold + "30" }]} testID="daily-reward-error">
        <View style={styles.errorContent}>
          <Feather name="alert-circle" size={16} color={colors.destructive} />
          <Text style={[styles.errorText, { color: colors.destructive }]}>Failed to load reward</Text>
        </View>
        <Pressable 
          style={[styles.retryBtn, { backgroundColor: colors.input }]}
          onPress={() => refreshDailyReward()}
          accessibilityRole="button"
          accessibilityLabel="Retry loading daily reward"
          testID="daily-reward-retry"
        >
          <Feather name="refresh-cw" size={14} color={colors.foreground} />
        </Pressable>
      </View>
    );
  }
  
  if (!dailyReward) return null;

  return (
    <View style={[styles.container, { backgroundColor: colors.card, borderColor: colors.gold + "30" }]} testID="daily-reward-banner">
      <View style={[styles.cardBgGlow, { backgroundColor: colors.gold }]} />
      
      <View style={styles.cardInner}>
        {/* Left Medallion */}
        <Animated.View style={[styles.medallionWrap, animatedMedallionStyle]}>
          <Animated.View style={[styles.medallionGlow, { backgroundColor: colors.gold }, animatedGlowStyle]} />
          <StarBadge stars={5} size="md" />
        </Animated.View>

        {/* Right Content */}
        <View style={styles.cardMain}>
          <View style={styles.headerRow}>
            <View style={styles.titleGroup}>
              <Text style={[styles.dailyGiftTitle, { color: colors.gold }]}>DAILY GIFT</Text>
              <Text style={[styles.amountTitle, { color: colors.foreground }]}>5 Star Coins</Text>
            </View>
            <View style={styles.actionGroup}>
              {dailyReward.available && !dailyReward.claimed ? (
                <Pressable
                  style={({ pressed }) => [
                    styles.claimBtn,
                    { backgroundColor: colors.gold, opacity: pressed ? 0.8 : 1 }
                  ]}
                  onPress={handleClaimPress}
                  accessibilityRole="button"
                  accessibilityLabel="Claim 5 Star Coins"
                  testID="daily-reward-claim-btn"
                >
                  <Feather name="gift" size={14} color="#fff" />
                  <Text style={styles.claimBtnText}>Claim Gift</Text>
                </Pressable>
              ) : dailyReward.claimed ? (
                <View style={[styles.badge, { backgroundColor: colors.success + "15", borderColor: colors.success + "30" }]}>
                  <Feather name="check" size={12} color={colors.success} />
                  <Text style={[styles.badgeText, { color: colors.success }]}>Claimed</Text>
                </View>
              ) : null}
            </View>
          </View>

          <View style={styles.timingCol}>
            <Text style={[styles.subtitle, { color: colors.mutedForeground }]}>
              {dailyReward.claimed ? "Next reward: " : "Refreshes at "}{dailyReward.refreshTime}
            </Text>
            <Animated.Text
              style={[styles.timer, { color: colors.foreground }, animatedTimeStyle]}
              testID="daily-reward-timer"
            >
              Next reward in {timeLeft !== null ? formatTime(timeLeft) : "--:--:--"}
            </Animated.Text>
          </View>
        </View>
      </View>
      
      {/* Confirmation Modal */}
      <Modal
        visible={modalVisible}
        transparent
        animationType="fade"
        onRequestClose={() => !claiming && setModalVisible(false)}
        testID="daily-reward-modal"
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
            <View style={[styles.modalIconWrap, { backgroundColor: colors.gold + "18" }]}>
              <StarBadge stars={5} size="lg" />
            </View>
            <Text style={[styles.modalTitle, { color: colors.foreground }]}>Claim Daily Reward</Text>
            <Text style={[styles.modalBody, { color: colors.mutedForeground }]}>
              You are about to claim your 5 free Star Coins for today.
            </Text>
            
            {dailyRewardError && (
              <Text style={[styles.modalError, { color: colors.destructive }]}>{dailyRewardError}</Text>
            )}
            
            <View style={styles.modalActions}>
              <Pressable
                style={[styles.modalSecondary, { backgroundColor: colors.input }]}
                onPress={() => setModalVisible(false)}
                disabled={claiming}
                accessibilityRole="button"
                accessibilityLabel="Cancel claim"
                testID="daily-reward-cancel-btn"
              >
                <Text style={[styles.modalSecondaryText, { color: colors.foreground }]}>Cancel</Text>
              </Pressable>
              
              <Pressable
                style={[styles.modalPrimary, { backgroundColor: colors.gold, opacity: claiming ? 0.7 : 1 }]}
                onPress={handleConfirmClaim}
                disabled={claiming}
                accessibilityRole="button"
                accessibilityLabel="Claim 5 Star Coins"
                testID="daily-reward-confirm-btn"
              >
                {claiming ? (
                  <ActivityIndicator color="#fff" size="small" />
                ) : (
                  <Text style={styles.modalPrimaryText}>Claim 5 Star Coins</Text>
                )}
              </Pressable>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginHorizontal: 16,
    marginBottom: 16,
    borderRadius: 20,
    borderWidth: 1,
    minHeight: 76,
    justifyContent: "center",
    overflow: "hidden",
  },
  cardBgGlow: {
    position: "absolute",
    top: -40,
    left: -20,
    width: 120,
    height: 120,
    borderRadius: 60,
    opacity: 0.08,
  },
  cardInner: {
    flexDirection: "row",
    padding: 16,
    gap: 16,
    alignItems: "center",
  },
  medallionWrap: {
    justifyContent: "center",
    alignItems: "center",
  },
  medallionGlow: {
    position: "absolute",
    top: -6,
    left: -6,
    right: -6,
    bottom: -6,
    borderRadius: 100,
  },
  cardMain: {
    flex: 1,
    gap: 12,
  },
  headerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: 8,
  },
  titleGroup: {
    flex: 1,
    gap: 2,
  },
  dailyGiftTitle: {
    fontFamily: "Inter_700Bold",
    fontSize: 11,
    letterSpacing: 0.5,
  },
  amountTitle: {
    fontFamily: "Inter_700Bold",
    fontSize: 16,
  },
  actionGroup: {
    justifyContent: "flex-start",
  },
  claimBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 10,
  },
  claimBtnText: {
    fontFamily: "Inter_600SemiBold",
    fontSize: 13,
    color: "#fff",
  },
  badge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
  },
  badgeText: {
    fontFamily: "Inter_600SemiBold",
    fontSize: 12,
  },
  timingCol: {
    gap: 2,
  },
  subtitle: {
    fontFamily: "Inter_400Regular",
    fontSize: 13,
  },
  timer: {
    fontFamily: "Inter_600SemiBold",
    fontSize: 13,
    fontVariant: ["tabular-nums"],
  },
  errorContent: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    padding: 16,
  },
  errorText: {
    fontFamily: "Inter_500Medium",
    fontSize: 14,
  },
  retryBtn: {
    position: "absolute",
    right: 16,
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: "center",
    justifyContent: "center",
  },
  
  // Modal styles
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.5)",
    justifyContent: "center",
    alignItems: "center",
    padding: 24,
  },
  modalCard: {
    width: "100%",
    maxWidth: 340,
    borderRadius: 20,
    borderWidth: 1,
    padding: 24,
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.1,
    shadowRadius: 20,
    elevation: 10,
  },
  modalIconWrap: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 16,
  },
  modalTitle: {
    fontFamily: "Inter_700Bold",
    fontSize: 18,
    marginBottom: 8,
    textAlign: "center",
  },
  modalBody: {
    fontFamily: "Inter_400Regular",
    fontSize: 14,
    textAlign: "center",
    marginBottom: 24,
    lineHeight: 20,
  },
  modalError: {
    fontFamily: "Inter_500Medium",
    fontSize: 13,
    textAlign: "center",
    marginBottom: 16,
  },
  modalActions: {
    flexDirection: "row",
    gap: 12,
    width: "100%",
  },
  modalSecondary: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
  },
  modalSecondaryText: {
    fontFamily: "Inter_600SemiBold",
    fontSize: 15,
  },
  modalPrimary: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
  },
  modalPrimaryText: {
    fontFamily: "Inter_600SemiBold",
    fontSize: 15,
    color: "#fff",
  },
});
"""

with open("artifacts/mobile/components/DailyRewardBanner.tsx", "w") as f:
    f.write(head + new_tail)

