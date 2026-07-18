"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var vue_1 = require("vue");
require("./style.css");
var App_vue_1 = require("./App.vue");
var pinia_1 = require("pinia");
var router_1 = require("./router");
(0, vue_1.createApp)(App_vue_1.default).use((0, pinia_1.createPinia)()).use(router_1.default).mount('#app');
