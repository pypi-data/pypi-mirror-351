import { VueSSRApp } from "vue-ssr-service";
import HelloWorld from "./components/HelloWorld.vue";

export const ssrApp = new VueSSRApp(HelloWorld);

ssrApp.mount("user-greeting");
