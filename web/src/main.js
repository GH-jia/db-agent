import { createApp } from "vue";
import ElementPlus from "element-plus";
import * as ElementPlusIconsVue from "@element-plus/icons-vue";
import App from "./App.vue";
import "element-plus/dist/index.css";
import "./styles.css";

const app = createApp(App);

app.use(ElementPlus);
Object.entries(ElementPlusIconsVue).forEach(([key, component]) => {
  app.component(key, component);
});

app.mount("#app");
