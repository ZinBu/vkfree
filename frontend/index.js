var need_register_style = 'text-align: center; padding-top: 150px;';
var TASK_DELAY = 3500;

//TODO Сделать, чтобы не дергалась статика
Vue.component('temp-loader', {
  template: `
  <div class="container">
        <div class="item-1"></div>
        <div class="item-2">
        </div><div class="item-3">
        </div><div class="item-4">
        </div><div class="item-5">
  </div></div>
  `
})
Vue.component('request-button', {
  props: ['func', 'wip', 'btn_name'],
  template: `
  <a v-if="!wip" v-on:click='func' style="cursor: pointer;" class="welcome-button js-download-button"> <span class="octicon octicon-move-down"></span>{{ btn_name }}</a>
  <a v-else class="welcome-button js-download-button"> <span class="octicon octicon-move-down"></span>{{ btn_name }}</a>
  `
})

var app = new Vue({
  el: '#app',
  data: {
    first_name: 'Пользователь',
    photo_link: '',
    root_app_href: '',
    user_is_login: false,
    init_auth: false,
    display_entry_button: false,
    welcome_style: need_register_style,
    user_stats: null,
    wip: false,
    task_msg: null,
    extended_token: '',
    extend_token_result: '',
    clearing_in_progress: false
  },
  methods: {
        requestData: function () {
             axios.get('/api/welcome/')
                .then(response => (
                    this.first_name = response.data.first_name,
                    this.photo_link = response.data.photo_link,
                    this.root_app_href = response.data.root_app_href,
                    this.user_is_login = true,
                    this.welcome_style = ''
                ))
                .catch(
                    error => this.display_entry_button = true
                );
        },
        logout: function () {
             axios.get('api/logout/')
                .then(response => (
                    this.display_entry_button = true,
                    this.user_is_login = false,
                    this.user_stats = null,
                    this.welcome_style = need_register_style
                ))
                .catch(error => {});
        },
        login: function () {
            this.init_auth = true;
            window.open('api/auth/', '_self');
        },
        requestStatistic: function () {
             this.wip = true;
             axios.get('/api/get_statistic/')
                .then(response => (
                    this.user_stats = response.data,
                    this.wip = false
                ))
                .catch(error => {this.wip = false;});
        },
        requestIntervalStatistic: function () {
            if (!this.wip && this.user_stats !== null && this.clearing_in_progress === true) {
                this.requestStatistic()
            }
        },
        turnOfExtendMsg: function () {this.extend_token_result = ""},
        sendToken: function () {
             this.wip = true;
             axios.post('/api/send_token/', {token: this.extended_token})
                .then(response => {
                    this.extend_token_result = "Успешно!!!";
                    this.extended_token = "";
                    this.wip = false;
                    setTimeout(this.turnOfExtendMsg, TASK_DELAY);
                })
                .catch(error => {
                    this.extend_token_result = "Не удалось!!!";
                    this.wip = false;
                    setTimeout(this.turnOfExtendMsg, TASK_DELAY);
                });
        },
        turnOfTaskStatus: function () {this.task_msg = null},
        clearData: function (category) {
            this.wip = true;
            this.clearing_in_progress = true;
            axios.post('/api/clear/', {kind: category})
                .then(response => {
                    this.task_msg = 'Задача в работе!';
                    this.wip = false;
                    setTimeout(this.turnOfTaskStatus, TASK_DELAY);
                })
                .catch(error => {
                    this.task_msg = 'Нельзя поставить задачу, пока выполняется другая. Попробуй позже!';
                    this.wip = false;
                    setTimeout(this.turnOfTaskStatus, TASK_DELAY);
                });
        },
        isDisabled: function (field) {
             return ['Недоступно!', 0].includes(this.user_stats[field]);
        },
        isUnreachable: function () {
            if (this.user_stats !== null){
                     for (prop in this.user_stats) {
                          if (this.user_stats[prop] === 'Недоступно!'){
                                return true
                          };
                        };
                     };
        }
 },
//  beforeMount(){
//     this.requestData()
// },
 mounted(){
    this.requestData();
    setInterval(this.requestIntervalStatistic, 15000);
 }
})