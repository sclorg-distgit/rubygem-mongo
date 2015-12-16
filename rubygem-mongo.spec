%{!?scl:%global pkg_name %{name}}
%{?scl:%scl_package rubygem-%{gem_name}}
%global gem_name mongo

%{!?enable_test: %global enable_test 0%{!?scl:1}}

Summary:       Ruby driver for the MongoDB
Name:          %{?scl:%scl_prefix}rubygem-%{gem_name}
Version:       1.9.2
Release:       1%{?dist}
License:       ASL 2.0
URL:           http://www.mongodb.org
Source0:       http://rubygems.org/gems/%{gem_name}-%{version}.gem
Requires:      %{?scl_prefix_ruby}ruby(release)
Requires:      %{?scl_prefix_ruby}ruby(rubygems)
Requires:      %{?scl_prefix}rubygem(bson) = %{version}
BuildRequires: %{?scl_prefix_ruby}ruby(release)
BuildRequires: %{?scl_prefix_ruby}rubygems-devel
%if 0%{enable_test} > 0
# For running the tests
# TODO: customize mongo collection prefix: >bkabrda< %{?scl:%scl_require_package sclname foo}%{!?scl:foo}
BuildRequires: %{?scl:mongodb24-}mongodb-server
BuildRequires: %{?scl_prefix}rubygem(bson)
# Shoulda is missing in SCL.
BuildRequires: %{?scl_prefix}rubygem(shoulda)
BuildRequires: %{?scl_prefix}rubygem(mocha)
BuildRequires: %{?scl_prefix_ruby}rubygem(minitest)
%endif
BuildArch:     noarch
Provides:      %{?scl_prefix}rubygem(%{gem_name}) = %{version}


%description
A Ruby driver for MongoDB. For more information about Mongo, see
http://www.mongodb.org.

%package doc
Summary: Documentation for %{name}
Requires: %{name} = %{version}-%{release}

%description doc
Documentation for %{name}


%prep
%{?scl:scl enable %scl - << \EOF}
gem unpack %{SOURCE0}
%setup -q -D -T -n  %{gem_name}-%{version}

gem spec %{SOURCE0} -l --ruby > %{gem_name}.gemspec

chmod a-x test/test_helper.rb
%{?scl:EOF}

%build
mkdir -p .%{gem_dir}
%{?scl:scl enable %scl - << \EOF}
# Create the gem as gem install only works on a gem file
gem build %{gem_name}.gemspec

%gem_install
%{?scl:EOF}

%install
mkdir -p %{buildroot}%{gem_dir}
cp -a .%{gem_dir}/* %{buildroot}%{gem_dir}/

mkdir -p %{buildroot}%{_bindir}
cp -a .%{_bindir}/* %{buildroot}%{_bindir}

%if 0%{enable_test} > 0
%check
pushd .%{gem_instdir}

# Lets go with minitest.
sed -i "/gem 'test-unit'/ d" test/test_helper.rb
sed -i "s|assert_true|assert|" test/functional/uri_test.rb
sed -i "s|assert_false|refute|" test/sharded_cluster/basic_test.rb

# Spawn For Ruby 1.8 should not be needed for Ruby 1.9+.
sed -i "/require 'sfl'/ d" test/tools/mongo_config.rb

# No shoulda in SCL.
%{?scl: sed -i "/require 'shoulda'/ d" test/test_helper.rb}

# TODO: mongo prefix
%{?scl:scl enable mongodb24 %scl - << \EOF}

# Create data directory and start testing mongo instance.
mkdir data
mongod \
  --dbpath data \
  --logpath data/log \
  --fork \
  --auth

# Create the gem as gem install only works on a gem file
# This should mimic the "rake test:default".
# https://github.com/mongodb/mongo-ruby-driver/blob/1.9.2/tasks/testing.rake
find test/{unit,functional,threading} -name '*_test.rb' \
  ! -wholename 'test/functional/grid_io_test.rb' \
  ! -wholename 'test/functional/grid_test.rb' \
  ! -wholename 'test/functional/ssl_test.rb' \
  | DBPATH=data xargs testrb -Ilib:test

# Shutdown mongo and celanupt the data.
mongod --shutdown --dbpath data
rm -rf data

%{?scl:EOF}
popd
%endif

%files
%doc %{gem_instdir}/LICENSE
%dir %{gem_instdir}
%{_bindir}/mongo_console
%{gem_instdir}/bin
%{gem_libdir}
%{gem_spec}
%exclude %{gem_cache}

%files doc
%doc %{gem_instdir}/README.md
%doc %{gem_instdir}/VERSION
%doc %{gem_docdir}
%{gem_instdir}/test
%{gem_instdir}/mongo.gemspec
%{gem_instdir}/Rakefile

%changelog
* Tue Nov 19 2013 Vít Ondruch <vondruch@redhat.com> - 1.9.2-1
- Update to mongo 1.9.2.
- Enabled test suite for non-SCL builds.

* Mon Aug 26 2013 Troy Dawson <tdawson@redhat.com> - 1.9.1-2
- Release bump

* Mon Jan 14 2013 Troy Dawson <tdawson@redhat.com> - 1.9.1-1
- Updated to version 1.9.1

* Mon Jan 14 2013 Troy Dawson <tdawson@redhat.com> - 1.8.1-1
- Updated to version 1.8.1

* Thu Nov 08 2012 Troy Dawson <tdawson@redhat.com>  - 1.7.0-3
- Packaged to work with SCL

* Tue Oct 09 2012 Troy Dawson <tdawson@redhat.com> - 1.7.0-1
- Updated to version 1.7.0

* Fri Aug 10 2012 Troy Dawson <tdawson@redhat.com> - 1.6.4-2
- Fixed doc
- removed more BuildRequires that are not required

* Thu Aug 09 2012 Troy Dawson <tdawson@redhat.com> - 1.6.4-1
- Updated to latest version
- Removed BuildRequires that are not needed

* Thu Aug 09 2012 Troy Dawson <tdawson@redhat.com> - 1.4.0-7
- Fixed checks.  
  Only run checks that do not require a running mongodb server

* Tue Aug 07 2012 Troy Dawson <tdawson@redhat.com> - 1.4.0-6
- Changed .gemspec and Rakefile to not be doc
- Added checks

* Thu Aug 02 2012 Troy Dawson <tdawson@redhat.com> - 1.4.0-5
- Fixed rubygem(bson) requires

* Mon Jul 23 2012 Troy Dawson <tdawson@redhat.com> - 1.4.0-4
- Updated to meet new fedora rubygem guidelines

* Thu Nov 17 2011 Troy Dawson <tdawson@redhat.com> - 1.4.0-3
- Changed group to Development/Languages
- Changed the global variables
- Seperated the doc and test into the doc rpm

* Thu Nov 17 2011 Troy Dawson <tdawson@redhat.com> - 1.4.0-2
- Added %{?dist} to version

* Tue Nov 15 2011  <tdawson@redhat.com> - 1.4.0-1
- Initial package
