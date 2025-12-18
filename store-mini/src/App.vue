<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();

onLaunch(() => {
  console.log("App Launch");
  // Check if user is logged in
  if (!userStore.isLoggedIn) {
    console.log("User not logged in, attempting silent login...");
    userStore.login().catch(err => {
      console.error("Silent login failed:", err);
    });
  } else {
    console.log("User already logged in");
  }
});
onShow(() => {
  console.log("App Show");
});
onHide(() => {
  console.log("App Hide");
});
</script>
<style></style>
