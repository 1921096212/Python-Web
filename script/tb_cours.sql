insert into tb_teachers (name, positional_title, profile, avatar_url, create_time, update_time, is_delete) values
('蓝羽', 'python高级讲师', '讲师简介', '/static/media/avatar.jpeg', now(), now(), 0);


insert into tb_course_category (name, create_time, update_time, is_delete) values
('python基础', now(), now(), 0),
('python高级', now(), now(), 0),
('python框架', now(), now(), 0);


insert into tb_course (title, cover_url, video_url, duration, `profile`, outline, teacher_id, category_id, create_time, update_time, is_delete) values
('香港',
'http://jjttn6vy531u0q6arc0.exp.bcevod.com/mda-jjtwsc7t6ax1zq4j/mda-jjtwsc7t6ax1zq4j.jpg',
'http://jjttn6vy531u0q6arc0.exp.bcevod.com/mda-jjtwsc7t6ax1zq4j/mda-jjtwsc7t6ax1zq4j.m3u8',
3.2, '你的测试视频简介', '你的视频大纲', 1, 2, now(), now(), 0);