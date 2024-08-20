document.addEventListener('DOMContentLoaded', function () {

    myData = window.myData;
    console.log(myData);

    var startTime = myData.startTime;
    var endTime = myData.endTime;

    flatpickr.localize(flatpickr.l10ns.zh);
    flatpickr('#set_zdy', {
        locale: flatpickr.l10ns.zh,
        enableTime: true,
        noCalendar: false,
        time_24hr: true,
        mode: "range",
        dateFormat: "Y-m-d",
        // onChange: function (selectedDates, dateStr, instance) {
        //     console.log("用户选择了日期:", selectedDates, "格式化后的日期字符串:", dateStr);
        //     // 在这里，你可以认为用户已经“选完了”日期
        // }
        onClose: function (selectedDates, dateStr, instance) {
            console.log("日期选择器关闭了，用户选择的日期（如果有）:", selectedDates, "格式化后的日期字符串:", dateStr);
            // 你可以在这里执行一些操作，因为用户已经完成了与日期选择器的交互
            // $('#starttime').html(selectedDates);
            if (dateStr !== '') {
                $("#starttime").html('');
                $("#endtime").html(" " + dateStr);
            }
            $('#set_zdy').hide();
        }
        // defaultDate: ["today", "tomorrow"],

    });
    let deleList = $('.date');

    deleList.click(function () {
        deleList.val('');
    });

    $('#select_week').click(function () {
        deleList.hide();
        deleList.val('')
        let week = $('#set_week');
        week.css({'display': 'block', "top": "25px", "width": "140px"});
        week.trigger('focus');
        // console.log(week.val());

    });
    $('#set_week').blur(function () {
        let time = $(this).val();
        console.log(time);
        console.log(typeof time)
        if (time !== '') {
            let date = weekTimestamps(time);
            let form_start = form_data(date.start);
            let form_end = form_data(date.end);
            $('#starttime').html(" " + form_start + " 至 ");
            $('#endtime').html(form_end);
        }
        deleList.hide();
    });

    $('#select_month').click(function () {
        deleList.hide();
        deleList.val('');
        let month = $('#set_month');
        month.css({'display': 'block', "top": "25px", "width": "100px"});
        month.trigger('focus');
        // console.log(month.val());
    });
    $('#set_month').blur(function () {
        let time = $(this).val();
        console.log(time);
        console.log(typeof time)
        if (time !== '') {
            let date = getMonthTimestamps(time);
            let form_start = form_data(date.start);
            let form_end = form_data(date.end);
            $('#starttime').html(" " + form_start + " 至 ");
            $('#endtime').html(form_end);
        }
        deleList.hide();
    });

    $('#select_zdy').click(function () {
        deleList.hide();
        deleList.val('');
        let zdy = $('#set_zdy');
        zdy.css({'display': 'block', "top": "25px", "width": "160px"});
        zdy.trigger('focus');
        // console.log(zdy.val());
    });


    $('.fixedDates').click(function () {
        let poi_id = $('#poi_id').val();
        let time = $(this).attr('data-time');
        let time_dic = calculateTimestamps(time);
        startTime = time_dic.start;
        endTime = time_dic.end;
        location.href = '/hangye/' + poi_id + '/' + startTime + '/' + endTime;
        console.log(startTime);
    })

    function weekTimestamps(isoWeekStr) {
        const [year, week] = isoWeekStr.split('-W').map(Number);
        const firstDayOfWeek = new Date(year, 0, 1 + (week - 1) * 7); // Monday of the given week
        const lastDayOfWeek = new Date(firstDayOfWeek.getTime() + 6 * 24 * 60 * 60 * 1000); // Sunday of the given week at 00:00:00

        // Set hours, minutes, seconds, and milliseconds to 0 for both dates
        firstDayOfWeek.setHours(0, 0, 0, 0);
        lastDayOfWeek.setHours(0, 0, 0, 0);

        return {
            start: Math.floor(firstDayOfWeek.getTime() / 1000),
            end: Math.floor(lastDayOfWeek.getTime() / 1000)
        };
    }

    function dateRangeToTimestamps(dateRange) {
        // 使用示例
        // let dateRange = "2023-09-01 至 2023-09-30";
        // let timestamps = dateRangeToTimestamps(dateRange);
        // const timestamps = getTimestampsForDateRange(startDateStr, endDateStr);
        //
        // console.log(timestamps);
        // 输出：{ start: 1696224000000, end: 1698816000000 } （具体值可能会根据运行环境有微小差异）
        // 创建Date对象
        var dates = dateRange.split(' 至 ');
        var startDate = new Date(dates[0]);
        var endDate = new Date(dates[1]);
        startDate.setHours(0, 0, 0, 0); // 设置时间为00:00:00
        endDate.setHours(12, 0, 0, 0); // 设置时间为00:00:00
        // 验证日期是否有效
        if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
            throw new Error('Invalid date string');
        }

        // 获取时间戳（毫秒）Math.floor(start.getTime() / 1000)
        const startTimestamp = Math.floor(startDate.getTime() / 1000);
        const endTimestamp = Math.floor(endDate.getTime() / 1000);

        // 返回包含时间戳的对象
        return {
            start: startTimestamp,
            end: endTimestamp
        };
    }

    function getMonthTimestamps(yearMonth) {
        const [year, month] = yearMonth.split('-');
        const startDate = new Date(year, month - 1); // 注意：JavaScript 中月份是从0开始的，所以需要减1
        const endDate = new Date(year, month, 0); // 设置天数为0会自动获取上个月的最后一天，这里正好是本月的最后一天

        // 将时间设置为每月的第一天和最后一天的开始和结束时刻
        startDate.setHours(0, 0, 0, 0); // 设置时间为00:00:00
        endDate.setHours(0, 0, 0, 0); // 设置时间为00:00:00

        // 获取时间戳（毫秒级），然后转换为秒级
        const startTimestamp = Math.floor(startDate.getTime() / 1000);
        const endTimestamp = Math.floor(endDate.getTime() / 1000);

        return {
            start: startTimestamp,
            end: endTimestamp
        };
    }

    function calculateTimestamps(daysBack) {
        // 使用示例
        // const {startTime, endTime} = calculateTimestamps(7);
        // console.log(`Start time: ${start}`);
        // console.log(`End time: ${end}`);
        // 将基准日期字符串转换为Date对象
        const baselineDate = new Date(); // 假设基准日期是当前日期的前一天;

        // 计算基准日期前daysBack天的日期
        const startDate = new Date(baselineDate);
        startDate.setDate(startDate.getDate() - daysBack);

        // 计算基准日期本身
        const endDate = new Date(baselineDate);
        startDate.setHours(0, 0, 0, 0); // 设置时间为00:00:00
        endDate.setHours(0, 0, 0, 0); // 设置时间为00:00:00

        // 转换为时间戳
        const startTimeStamp = Math.floor(startDate.getTime() / 1000);
        const endTimeStamp = Math.floor(endDate.getTime() / 1000);

        // 返回结果
        return {start: startTimeStamp, end: endTimeStamp};
    }

    function form_data(timestamps) {
        // 创建Date对象
        let date = new Date(timestamps * 1000);

        // 转换为可视化时间
        // 这里使用了toISOString()作为示例，但你可以使用toLocaleString()、toLocaleDateString()等来获得更友好的格式
        let formattedDate = date.toLocaleString(); // 这将根据你的浏览器语言和设置显示日期和时间
        // 或者，你可以自定义格式
        let year = date.getFullYear();
        let month = String(date.getMonth() + 1).padStart(2, '0'); // 月份是从0开始的
        let day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;

    }

    $("#starttime").html(form_data(startTime) + " 至 ");
    $("#endtime").html(form_data(endTime));

    $("#defaultButton").click(function () {
        console.log("sss");
        let poi_id = $('#poi_id').val();
        let zdy_time = $('#set_zdy').val();
        let week_time = $('#set_week').val();
        let month_time = $('#set_month').val();

        console.log("zdy_time" + zdy_time);
        console.log("week_time" + week_time);
        console.log("month_time" + month_time);

        // 如果startTime为空，则设置为2024年5月20日的秒级时间戳
        if (!startTime) {
            const startDateTime = new Date(2024, 4, 20); // 注意：月份是从0开始的，所以5月是4
            startTime = Math.floor(startDateTime.getTime() / 1000);
        }

        // 如果endTime为空，则设置为当前日期的秒级时间戳
        if (!endTime) {
            const endDateTime = new Date();
            endTime = Math.floor(endDateTime.getTime() / 1000);
        }

        if (startTime > endTime) {
            alert('开始时间要小于结束时间')
        } else {
            if (poi_id === "") {
                poi_id = '10747973'
            }

            if (zdy_time !== "") {
                let zdy_time_dic = dateRangeToTimestamps(zdy_time);
                startTime = zdy_time_dic.start;
                endTime = zdy_time_dic.end;
                location.href = '/hangye/' + poi_id + '/' + startTime + '/' + endTime;

            } else if (week_time !== "") {

                let week_time_dic = weekTimestamps(week_time);
                startTime = week_time_dic.start;
                endTime = week_time_dic.end;
                location.href = '/hangye/' + poi_id + '/' + startTime + '/' + endTime;

            } else if (month_time !== "") {
                let month_time_dic = getMonthTimestamps(month_time);
                startTime = month_time_dic.start;
                endTime = month_time_dic.end;

                location.href = '/hangye/' + poi_id + '/' + startTime + '/' + endTime;

            } else {
                // console.log('ss');

                location.href = '/hangye/' + poi_id + '/' + startTime + '/' + endTime;

            }
            console.log(startTime);
            console.log(endTime);
        }
    })


});





