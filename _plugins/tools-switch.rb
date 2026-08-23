# frozen_string_literal: true

# 工具模块硬开关（L2）
#
# 当 _config.yml 中 tools.enabled 为 false 时，在 post_read 钩子里把工具相关页面
# 从 site.pages 中移除，构建产物中彻底不出现 /tools/ 页面与 /tabs/tools/ 落地页。
# 侧边栏「工具」入口由 _includes/sidebar.html 中的守卫同步隐藏。
#
# 工具模块与博客核心的唯一接触点：
#   - _data/tabs.yml / tabs_en.yml 中的「工具」条目（3 行）
#   - _includes/sidebar.html 中的 hidden 守卫（约 5 行）
#   - _config.yml 中的 tools 开关块与本插件的加载
# 彻底下线工具模块：删除 tools/、assets/tools/、_data/tools.yml、_plugins/tools-switch.rb
# 及上述三处接入点即可，不影响博客其它功能。

Jekyll::Hooks.register :site, :post_read do |site|
  tools_config = site.config['tools']
  next unless tools_config.is_a?(Hash) && tools_config['enabled'] == false

  landing = ['tabs/tools.md', 'tabs/tools-en.md']

  removed = site.pages.reject! do |page|
    landing.include?(page.path) || page.path.to_s.start_with?('tools/')
  end

  # 清空工具注册表，防止其它模板意外引用
  site.data['tools'] = [] if site.data.is_a?(Hash)
  site.data['tools_en'] = [] if site.data.is_a?(Hash)

  Jekyll.logger.info('ToolsSwitch:', '已禁用（tools.enabled=false），工具页面不参与构建') if removed
end
