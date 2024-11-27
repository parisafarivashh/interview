# tasks



   
- 
   - [x]    ایجاد دیتابیس و import داده های transaction 
   - [x]  ستاپ اولیه و ساخت پروژه + Docker
   - [x] اتصال جنگو به منگو 
   - [x] پیاده سازی Pipelines Aggregation که modeو type را پشتیبانی کنند.
   - [x] پیاده سازی Api که خروجی مرحله قبل را در قالب ذکر شده برگرداند
   - [X] پیاده سازی یک کامند برای کش کردن اطالعات موجود در transaction
   - [X] پیاده سازی یک API که همان خروجی ذکر شده را با استفاده از داده های کش شده بهینه تر برگرداند.
   - [X]  پیادهسازی کالسهای مربوطه برای اعالن و APIهای مربوطه.
   - [X] پیادهسازی توابع ارسال اعالن برای هر Medium - در نهایت صرفا اطالعات اعالن به همراه نوع Medium چاپ بشه.
   - [X] پیادهسازی منطق تعریف قالب هر پیام
   - [X] ایجاد یک کامند یا تسک که ساعت ۲۴ هرروز گزارش تراکنش های اون روز مرچنت رو براش ارسال کنه
   - [X] ساخت Postman برای APIها


data structure transaction_summary

```commandline
Set the amount and count grouped by daily, weekly, or monthly intervals without specifying a merchant_id
[
     {
         _id: {value_mode: '1402/7/30' },
          count: 49,
          amount: Long('24466836100'),
          type_mode: 'daily'
      },
      ...
]

Set the amount and count grouped by daily, weekly, or monthly intervals for a specific merchant_id
[
    {   
    _id: {
        value_mode: '1402/11/8',
        merchantId: ObjectId('63a69a2d18f9347bd89d5f76')
        },
    count: 5,
    amount: Long('2226342800'),
    type_mode: 'daily'
    },
    ...

]



```
