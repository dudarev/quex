## About

**Quex** is a platform to get community questions answered. 
It helps collecting answers in various channels the community uses
(web, social networks, messaging apps and others).
It also re-broadcasts to multiple channels to get questions seen by many.


## Version 0.1

* Admin can see config.                                              `/admin/config GET`
* Admin can edit config.                                             `/admin/config/edit GET, POST`
* Admin can see all connected channels.                              `/admin/channel GET`
* Admin can create in-channel from vkontakte user wall posts.        `/admin/channel/add GET, POST`
* Admin can create in-channel from vkontakte group posts.            `/admin/channel/add GET, POST`
* Admin can connect Twitter account.                                 `/admin/channel/add GET, POST`
* Admin can see any channel.                                         `/admin/channel/<channel_id> GET`
* Admin can edit any channel.                                        `/admin/channel/<channel_id>/edit GET, POST`
* Admin can delete any channel.                                      `/admin/channel/<channel_id>/delete GET, POST`
* The wall posts are periodically loaded and stored.                 `cron`
* The comments to questions are periodically loaded and stored.      `cron`
* Comments for questions are periodically re-loaded.                 `cron`
* User can see all posts in reverse chronological order.             `/?start=<start> GET`
* User can search all questions.                                     `/search?q=<query>&start=<start> GET`
* User can see a question with comments.                             `/q/<question_id> GET`
* User can paginate comments.                                        `/q/<question_id>?start=<start> GET`
* Posts with questions marks are broadcasted to Twitter out-channel. `cron`
* Data is collected in Google Analytics.


## Future plans

* Vote for questions.
* Ask questions.
* Moderate questions.
* Tags.
* Question wiki.
* General wiki.
